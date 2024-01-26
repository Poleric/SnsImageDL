API Reference
=============

```python
class Extractor:
    async def __aenter__     (self)
    async def __aexit__      (self)
        
    def check_link           (cls , webpage_url: str) -> bool
    async def get_all_media  (self, webpage_url: str) -> Iterable[Media]
        

class Media:
    content: bytes
    filename: str
    tags: Tag
    
    def guess_extension  (self) -> str | None
    def add_metadata     (self) -> None
    def save             (self, output_directory: PathLike, *, add_metadata: bool = True) -> None

        
class Tag(TypedDict):
    title: str
    description: str
    webpage_url: str
    source_url: str
    created_at: str
    artist: {
        name: str
        display_name: str
        webpage_url: str
    }
    keywords: Sequence[str]
    type: Sequence[str]

def add_exif          (data: bytes, tag: Tag, *, extension: str = None) -> bytes
def add_jpeg_comment  (data: bytes, tag: Tag, *, extension: str = None) -> bytes
def add_xmp           (data: bytes, tag: Tag, *, extension: str = None) -> bytes

def get_matching_extractor  (query: str) -> Type[Extractor] | None
async def save_media        (query: str) -> None

```