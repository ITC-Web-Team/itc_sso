from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Project


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        # List of URL names for static pages
        return ['home', 'login', 'register', 'docs']

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    """Sitemap for verified projects"""
    changefreq = 'daily'
    priority = 0.6

    def items(self):
        # Only include verified projects in sitemap
        return Project.objects.filter(is_verified=True)

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        # Link to the project's main URL
        return f'/project/{obj.id}/ssocall/'

