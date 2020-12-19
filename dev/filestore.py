import os
import shutil

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage


class StorageError(Exception):
    pass


class OverwriteStorage:
    def save(self, name, content, max_length=None):
        if name == '':
            raise StorageError()
        if self.exists(name):
            self.delete(name)
        return super().save(name, content, max_length)


class LocalStorage(OverwriteStorage, FileSystemStorage):
    def clear(self):
        try:
            shutil.rmtree(self.location)
        except FileNotFoundError:
            pass


class PublicLocalStorage(LocalStorage):
    location = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_BUCKET, settings.PUBLIC_LOCATION)
    base_url = '/{}/{}/'.format(settings.MEDIA_BUCKET, settings.PUBLIC_LOCATION)


class PrivateLocalStorage(LocalStorage):
    location = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_BUCKET, settings.PRIVATE_LOCATION)
    base_url = '/{}/{}/'.format(settings.MEDIA_BUCKET, settings.PRIVATE_LOCATION)


class RemoteStorage(OverwriteStorage, S3Boto3Storage):
    def clear(self):
        self.bucket.objects.delete()

    def url(self, name, parameters=None, expire=None):
        url = super().url(name, parameters, expire)
        if settings.AWS_S3_OVERRIDE_URL:
            url = url.replace(settings.AWS_S3_ENDPOINT_URL, settings.AWS_S3_OVERRIDE_URL)
        return url


class StaticRemoteStorage(RemoteStorage):
    bucket_name = settings.STATIC_BUCKET
    location = settings.VERSION
    querystring_auth = False


class PublicRemoteStorage(RemoteStorage):
    bucket_name = settings.MEDIA_BUCKET
    location = settings.PUBLIC_LOCATION
    querystring_auth = False


class PrivateRemoteStorage(RemoteStorage):
    bucket_name = settings.MEDIA_BUCKET
    location = settings.PRIVATE_LOCATION
    querystring_auth = True
