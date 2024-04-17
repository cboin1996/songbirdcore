from pydantic import BaseModel
from typing import Optional, Union


class ItunesApiSongModel(BaseModel):
    trackName: str
    """specifies song name"""
    artistName: str
    """specifies song artist name"""
    collectionName: str
    """specifies album name"""
    artworkUrl100: str
    """specifies url pointing to album artwork"""
    primaryGenreName: str
    """specifies genre name for the song"""
    trackNumber: int
    """specifies song number in album"""
    trackCount: int
    """specifies number of songs in album"""
    collectionId: Union[int, str] = ""
    """specifies id for the album"""
    collectionArtistName: str = ""
    """specifies artist name for the album"""
    discNumber: int
    """specifies disc number in album"""
    discCount: int
    """specifies disc count in album"""
    releaseDate: str
    """specifies release date of album"""
    releaseDateKey: str = "releaseDate"
    """specifies key expected for releaseDate field in itunes api response object"""


class ItunesApiAlbumKeys(BaseModel):
    artistName: str
    """ specifies artist name for album"""
    collectionName: str
    """ specifies artist name for collection"""
    trackCount: int
    """ specifies number of songs in album"""
    collectionId: Union[int, str] = ""
    """ specified itunes api collection id"""
