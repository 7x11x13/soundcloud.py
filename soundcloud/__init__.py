from soundcloud.resource.aliases import (Like, RepostItem, SearchItem,
                                         StreamItem)
from soundcloud.resource.comment import Comment, CommentSelf, CommentTrack
from soundcloud.resource.conversation import Conversation
from soundcloud.resource.download import OriginalDownload
from soundcloud.resource.like import PlaylistLike, TrackLike
from soundcloud.resource.message import Message
from soundcloud.resource.playlist import (AlbumPlaylist, AlbumPlaylistNoTracks,
                                          BasicAlbumPlaylist)
from soundcloud.resource.stream import (PlaylistStreamItem,
                                        PlaylistStreamRepostItem,
                                        TrackStreamItem, TrackStreamRepostItem)
from soundcloud.resource.track import (BasicTrack, CommentTrack, Format, Media,
                                       MiniTrack, PublisherMetadata, Track,
                                       Transcoding)
from soundcloud.resource.user import (Badges, BasicUser, CreatorSubscription,
                                      Product, User)
from soundcloud.resource.visuals import Visual, Visuals
from soundcloud.resource.web_profile import WebProfile
from soundcloud.soundcloud import SoundCloud

__version__ = "1.3.7"
