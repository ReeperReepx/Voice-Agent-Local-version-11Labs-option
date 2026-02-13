"""Streaming ASR with faster-whisper.

Uses faster-whisper (CTranslate2) for transcription with partial transcripts.
Handles English, Hindi, and mixed Hinglish input.
No language locking — ASR always accepts all languages.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Optional

from .lang_detection import detect_language


@dataclass
class TranscriptSegment:
    """A segment of transcribed speech."""
    text: str
    is_partial: bool
    language: str  # "en", "hi", or "mixed"
    start_time: float = 0.0
    end_time: float = 0.0
    confidence: float = 0.0


@dataclass
class StreamingASR:
    """Streaming ASR using faster-whisper.

    Accumulates audio chunks and produces partial/final transcripts.
    """
    sample_rate: int = 16000
    chunk_duration_s: float = 2.0
    _buffer: list = field(default_factory=list)
    _transcripts: list = field(default_factory=list)
    _total_duration: float = 0.0
    _transcriber: object = None

    def initialize(self, transcriber=None) -> None:
        """Initialize with faster-whisper model."""
        if transcriber is not None:
            self._transcriber = transcriber
        else:
            from .model_loader import load_model
            self._transcriber = load_model()

    def feed_audio(self, audio_chunk: np.ndarray) -> Optional[TranscriptSegment]:
        """Feed an audio chunk and get a partial transcript if available.

        Args:
            audio_chunk: numpy array of audio samples (float32, mono, 16kHz)

        Returns:
            TranscriptSegment if enough audio accumulated, None otherwise.
        """
        self._buffer.append(audio_chunk)
        chunk_samples = int(self.chunk_duration_s * self.sample_rate)
        total_samples = sum(len(c) for c in self._buffer)

        if total_samples >= chunk_samples:
            audio = np.concatenate(self._buffer)
            self._buffer = []

            segment = self._transcribe(audio)
            if segment:
                self._transcripts.append(segment)
                self._total_duration += len(audio) / self.sample_rate
            return segment

        return None

    def finalize(self) -> Optional[TranscriptSegment]:
        """Finalize remaining audio in buffer."""
        if not self._buffer:
            return None

        audio = np.concatenate(self._buffer)
        self._buffer = []

        segment = self._transcribe(audio, is_final=True)
        if segment:
            self._transcripts.append(segment)
        return segment

    def _transcribe(self, audio: np.ndarray, is_final: bool = False) -> Optional[TranscriptSegment]:
        """Transcribe an audio segment using faster-whisper."""
        if self._transcriber is None:
            raise RuntimeError("ASR not initialized. Call initialize() first.")

        try:
            # faster-whisper accepts numpy arrays directly (float32, 16 kHz)
            segments, info = self._transcriber.transcribe(
                audio,
                beam_size=5,
                language="en",
                vad_filter=True,
            )

            text = " ".join(seg.text for seg in segments).strip()

            if not text:
                return None

            lang = detect_language(text)

            return TranscriptSegment(
                text=text,
                is_partial=not is_final,
                language=lang,
                start_time=self._total_duration,
                end_time=self._total_duration + len(audio) / self.sample_rate,
            )
        except Exception as e:
            return TranscriptSegment(
                text=f"[ASR Error: {e}]",
                is_partial=not is_final,
                language="unknown",
            )

    def get_full_transcript(self) -> str:
        """Get the complete transcript from all segments."""
        return " ".join(s.text for s in self._transcripts if s.text)

    def get_all_segments(self) -> list[TranscriptSegment]:
        """Get all transcript segments."""
        return self._transcripts.copy()

    def reset(self) -> None:
        """Reset the ASR state for a new session."""
        self._buffer = []
        self._transcripts = []
        self._total_duration = 0.0
