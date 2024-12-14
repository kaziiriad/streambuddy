import logging
from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import Http404
from .services.storage import StorageService

class VideoPlayerView(TemplateView):
    template_name = 'core/player.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.kwargs.get('title')
        
        if not title:
            raise Http404("Video title is required")
            
        storage_service = StorageService()
        try:
            metadata = storage_service.get_metadata(title)
            if not metadata:
                raise Http404("Video not found")
                
            # Make sure we pass both safe title and display title
            context.update({
                'title': metadata.get('title'),  # This is the safe title for URLs
                'display_title': metadata.get('display_title', metadata.get('title')),
                'status': metadata.get('status'),
                'uploaded_at': metadata.get('uploaded_at')
            })
            return context
        except Exception as e:
            logging.error(f"Error loading video {title}: {str(e)}")
            raise Http404(f"Error loading video: {str(e)}")
        
        
class VideoListView(TemplateView):
    template_name = 'core/video_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        storage_service = StorageService()
        context['videos'] = storage_service.list_videos() or []  # Return empty list if None
        return context

class VideoUploadView(TemplateView):
    template_name = 'core/upload.html'
