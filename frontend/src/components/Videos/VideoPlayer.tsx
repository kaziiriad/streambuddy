import React, { useEffect, useRef } from 'react';
// @ts-ignore
import shaka from 'shaka-player';

interface VideoPlayerProps {
  dashUrl: string;
  title: string;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ dashUrl, title }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const playerRef = useRef<any>(null);

  useEffect(() => {
    if (videoRef.current) {
      // Install built-in polyfills to patch browser incompatibilities
      shaka.polyfill.installAll();

      // Check to see if the browser supports the basic APIs Shaka needs
      if (shaka.Player.isBrowserSupported()) {
        // Create a Player instance
        const player = new shaka.Player(videoRef.current);
        playerRef.current = player;

        // Listen for error events
        player.addEventListener('error', (event: any) => {
          console.error('Error code', event.detail.code, 'object', event.detail);
        });

        // Try to load a manifest
        player.load(dashUrl).catch((error: any) => {
          console.error('Error loading manifest', error);
        });
      } else {
        console.error('Browser not supported!');
      }
    }

    return () => {
      if (playerRef.current) {
        playerRef.current.destroy();
      }
    };
  }, [dashUrl]);

  return (
    <div className="w-full">
      <div className="relative bg-black rounded-lg overflow-hidden">
        <video
          ref={videoRef}
          className="w-full h-auto max-h-96 md:max-h-[500px]"
          controls
          poster="https://images.pexels.com/photos/1040160/pexels-photo-1040160.jpeg?auto=compress&cs=tinysrgb&w=800"
        />
      </div>
      <div className="mt-4">
        <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
      </div>
    </div>
  );
};

export default VideoPlayer;