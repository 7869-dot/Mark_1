import { useEffect, useRef, useCallback } from "react";

// Total number of extracted frames from the python script
const frameCount = 576;
const currentFrame = (index: number) => `/videos/frames/frame_${(index + 1).toString().padStart(4, "0")}.webp`;

const ScrollVideo = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef<number>(0);
  
  // Track target frame based on scroll position
  const targetFrameRef = useRef<number>(0);
  // Track current visual frame for interpolation
  const currentFrameRef = useRef<number>(0);

  // Cache images so they instantly paint
  const imagesRef = useRef<HTMLImageElement[]>([]);

  const calculateTargetFrame = useCallback(() => {
    const container = containerRef.current;
    if (!container) return;

    const rect = container.getBoundingClientRect();
    const scrollableHeight = container.offsetHeight - window.innerHeight;
    const scrolled = -rect.top;
    
    // Calculate progress between 0 and 1
    const progress = Math.max(0, Math.min(1, scrolled / scrollableHeight));
    
    // Calculate target frame index (from 0 to 575)
    targetFrameRef.current = progress * (frameCount - 1);
  }, []);

  const updateCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (canvas) {
        const ctx = canvas.getContext("2d");
        if (ctx) {
            // Linear Interpolation (Lerp) factor: lowers to smooth more, raises to stick closer to target
            const lerpFactor = 0.08;
            const diff = targetFrameRef.current - currentFrameRef.current;
            
            // Move current frame closer to target slowly (lerp)
            if (Math.abs(diff) > 0.05) {
                currentFrameRef.current += diff * lerpFactor;
            } else {
                currentFrameRef.current = targetFrameRef.current;
            }

            const frameIndex = Math.floor(currentFrameRef.current);
            const img = imagesRef.current[frameIndex];

            // If the image object is successfully loaded from the cache, draw it instantly
            if (img && img.complete && img.naturalWidth !== 0) {
                // Ensure canvas resolution matches the natural image resolution
                if (canvas.width !== img.width || canvas.height !== img.height) {
                    canvas.width = img.width;
                    canvas.height = img.height;
                }
                
                // Paint the frame
                ctx.drawImage(img, 0, 0);
            }
        }
    }
    
    rafRef.current = requestAnimationFrame(updateCanvas);
  }, []);

  // Preload all images rapidly in the background
  useEffect(() => {
    const loadImages = () => {
      for (let i = 0; i < frameCount; i++) {
        const img = new Image();
        img.src = currentFrame(i);
        imagesRef.current[i] = img;
      }
    };
    
    loadImages();
  }, []);

  useEffect(() => {
    const onScroll = () => {
        calculateTargetFrame();
    };
    
    // Initial calculation in case it's not at the top
    calculateTargetFrame();
    
    window.addEventListener("scroll", onScroll, { passive: true });
    
    // Initialize the smooth animation loop
    rafRef.current = requestAnimationFrame(updateCanvas);
    
    return () => {
      window.removeEventListener("scroll", onScroll);
      cancelAnimationFrame(rafRef.current);
    };
  }, [calculateTargetFrame, updateCanvas]);

  return (
    <div ref={containerRef} className="relative bg-black" style={{ height: "500vh" }}>
      <div className="sticky top-0 h-screen w-full overflow-hidden flex items-center justify-center">
        {/* CSS Object Cover will efficiently stretch/crop the canvas buffer to fill the screen without aspect ratio distortion */}
        <canvas
          ref={canvasRef}
          className="h-full w-full object-cover"
          style={{ willChange: "transform" }}
        />
      </div>
    </div>
  );
};

export default ScrollVideo;
