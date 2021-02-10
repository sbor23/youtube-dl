# coding: utf-8
from __future__ import unicode_literals
import json

from .common import InfoExtractor


class PlaySuisseIE(InfoExtractor):
    _MEDIA_URL = 'https://4bbepzm4ef.execute-api.eu-central-1.amazonaws.com/prod/graphql'
    _VALID_URL = r'https?://(?:www\.)?playsuisse\.ch/watch/(?P<id1>[0-9]+)(?:/(?:[0-9]+))?'
    _TESTS = [
        {
            'url': 'https://www.playsuisse.ch/watch/763211/0',
            'md5': '0d716b7a16c3e6ab784ef817ee9a20c1',
            'info_dict': {
                'id': '763211',
                'ext': 'mp4',
                'title': 'Wilder S01E01 - Knochen',
                'description': 'md5:8ea7a8076ba000cd9e8bc132fd0afdd8'
            }
        },
        {
            'url': 'https://www.playsuisse.ch/watch/808675/0',
            'md5': '7aa043e69fea5044db2da8bb58bca239',
            'info_dict': {
                'id': '808675',
                'ext': 'mp4',
                'title': 'Der Läufer',
                'description': 'md5:'
            }
        },
        {
            'url': 'https://www.playsuisse.ch/watch/817913/0',
            'md5': '50721c46ca0b3a9836eb61ecb0ed7097',
            'info_dict': {
                'id': '42',
                'ext': 'mp4',
                'title': 'Nr. 47 S01E01 - Die Einweihungsparty',
                'description': 'md5:'
            }
        }
    ]

    def get_media_data(self, media_id):
        response = self._download_json(
            self._MEDIA_URL,
            media_id,
            data=json.dumps({
                'operationName': 'AssetWatch',
                'query': self._GRAPHQL_QUERY,
                'variables': {
                    "dataset": None,
                    "locale": "de",
                    "assetId": media_id
                }
            }).encode('utf-8'))

        return response['data']['asset']

    def _real_extract(self, url):
        media_id = self._VALID_URL_RE.match(url).groups()[0]
        media_data = self.get_media_data(media_id)

        if media_data.get('seriesName'):
            title = '{} S{:02}E{:02} - {}'.format(
                media_data.get('seriesName'),
                int(media_data.get('seasonNumber')),
                int(media_data.get('episodeNumber')),
                media_data.get('name'))
        else:
            title = media_data['name']

        description = media_data.get('description')
        thumbnails = [
            {
                'id': thumb.get('id'),
                'url': thumb.get('url')
            }
            for key, thumb in media_data.items()
            if key.startswith('thumbnail') and thumb is not None
        ]

        formats = []

        for media in media_data['medias']:
            if media['type'] == 'HLS':
                formats.extend(self._extract_m3u8_formats(
                    media['url'],
                    media_id,
                    'mp4',
                    'm3u8_native',
                    m3u8_id="HTTP-HLS-HD",
                    fatal=False))

            elif media['type'] == 'DASH':
                continue

                # TODO seems to be 404 for all tested media
                # formats.extend(self._extract_mpd_formats(
                #     media['url'],
                #     media_id,
                #     mpd_id='dash',
                #     fatal=False
                # ))

        return {
            'id': media_id,
            'title': title,
            'description': description,
            'thumbnails': thumbnails,
            'formats': formats,
        }

    _GRAPHQL_QUERY = '''\
query AssetWatch($dataset: String, $locale: String!, $assetId: ID!) {
  asset(dataset: $dataset, locale: $locale, assetId: $assetId) {
    ...Asset
    __typename
  }
}

fragment Asset on Asset {
  ...AssetDetails
  episodes {
    ...AssetDetails
    __typename
  }
  __typename
}

fragment AssetDetails on Asset {
  audioLanguages
  awards
  bu
  contentCategories
  contentCodes
  contentTypes
  contractType
  countries
  creators
  description
  descriptionLong
  directors
  downloadable
  duration
  editorialContentCategoriesDatalab {
    id
    title
    __typename
  }
  editorialContentMetaCategoriesDatalab {
    id
    title
    __typename
  }
  endDate
  episodeNumber
  episodesInSequence
  externalId
  id
  image16x9 {
    ...ImageDetails
    __typename
  }
  image2x3 {
    ...ImageDetails
    __typename
  }
  image16x9WithTitle {
    ...ImageDetails
    __typename
  }
  image2x3WithTitle {
    ...ImageDetails
    __typename
  }
  mainCast
  name
  numberOfSeasons
  otherKeyPeople
  parentalRating
  popularity
  premium
  presenters
  primaryLanguage
  productionCompanies
  productionCountries
  provider
  ratings
  regions
  restrictions
  seasonNumber
  seriesId
  seriesName
  parentId
  startDate
  subtitleLanguages
  tagline
  targetAudience
  themes
  thumbnail16x9 {
    ...ImageDetails
    __typename
  }
  thumbnail2x3 {
    ...ImageDetails
    __typename
  }
  thumbnail16x9WithTitle {
    ...ImageDetails
    __typename
  }
  thumbnail2x3WithTitle {
    ...ImageDetails
    __typename
  }
  type
  writers
  year
  medias {
    ...MediaDetails
    __typename
  }
  trailerMedias {
    ...MediaDetails
    __typename
  }
  sponsors {
    ...SponsorDetails
    __typename
  }
  sponsorEndDate
  __typename
}

fragment ImageDetails on Image {
  id
  url
  alt
  __typename
}

fragment MediaDetails on Media {
  id
  type
  url
  duration
  __typename
}

fragment SponsorDetails on Sponsor {
  id
  name
  description
  type
  externalId
  image16x9 {
    ...ImageDetails
    __typename
  }
  thumbnail16x9 {
    ...ImageDetails
    __typename
  }
  __typename
}'''
