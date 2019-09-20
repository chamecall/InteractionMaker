from Enums import MediaType

class Media:

    media_type = {'I': MediaType.IMAGE,
                  'T': MediaType.TEXT,
                  'A': MediaType.AUDIO,
                  'V': MediaType.VIDEO}

    def __init__(self, file_name, m_type, duration):
        self.file_name = file_name
        self.duration = duration
        self.type = self.media_type[m_type]

