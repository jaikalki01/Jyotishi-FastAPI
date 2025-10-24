import enum

class SessionType(str, enum.Enum):
    chat = "chat"
    audio_call = "audio_call"
    video_call = "video_call"


class SessionStatus(str, enum.Enum):
    pending = "pending"       # Request created, waiting for astrologer
    accepted = "accepted"     # Astrologer accepted session
    declined = "declined"     # Astrologer declined session
    ongoing = "ongoing"       # Session in progress
    ended = "ended"           # Session finished normally
    cancelled = "cancelled"   # Cancelled before starting
