from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import Http404
from .services.storage import StorageService

class VideoPlayerView(TemplateView):
    template_name = 'core/player.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.kwargs.get('title')
        
        storage_service = StorageService()
        try:
            metadata = storage_service.get_metadata(title)
            if not metadata:
                raise Http404("Video not found")
                
            context.update({
                'title': metadata.get('title'),
                'status': metadata.get('status'),
                'uploaded_at': metadata.get('uploaded_at'),
            })
        except Exception as e:
            raise Http404(f"Error loading video: {str(e)}")
            
        return context

class VideoListView(TemplateView):
    template_name = 'core/video_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        storage_service = StorageService()
        context['videos'] = storage_service.list_videos()
        return context

