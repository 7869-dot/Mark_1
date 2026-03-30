import { useRef, useEffect, useCallback, useState } from "react";

const TOTAL_FRAMES = 576; // Using 576 to perfectly wrap up to the end

const ScrollVideo = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef<number>(0);
  
  // State to hold preloaded images
  const [images, setImages] = useState<HTMLImageElement[]>([]);
  // Store scroll target and current position for smooth lerp effect
  const scrollData = useRef({ target: 0, current: 0 });

  // Preload all 576 images in the background
  useEffect(() => {
    const loadedImages: HTMLImageElement[] = [];
    let loadedCount = 0;

    for (let i = 1; i <= TOTAL_FRAMES; i++) {
      const img = new Image();
      // frame_0001.webp syntax
      img.src = `/frames/frame_${i.toString().padStart(4, "0")}.webp`;
      img.onload = () => {
        loadedCount++;
        // Quick draw of frame 1 as soon as it's ready so canvas isn't blank
        if (i === 1) {
          const ctx = canvasRef.current?.getContext("2d");
          if (ctx) {
            ctx.canvas.width = window.innerWidth;
            ctx.canvas.height = window.innerHeight;
            ctx.drawImage(img, 0, 0, ctx.canvas.width, ctx.canvas.height);
          }
        }
        if (loadedCount === TOTAL_FRAMES) {
          setImages(loadedImages);
        }
      };
      loadedImages.push(img);
    }
  }, []);

  // Use requestAnimationFrame loop for continuous rendering & lerping
  const updateCanvas = useCallback(() => {
    // Lerp logic to smooth out the scroll jitters
    scrollData.current.current += (scrollData.current.target - scrollData.current.current) * 0.1;
    
    if (images.length === TOTAL_FRAMES && canvasRef.current) {
      const ctx = canvasRef.current.getContext("2d");
      if (ctx) {
        // Map 0 -> 1 progress to 0 -> TOTAL_FRAMES - 1
        const frameIndex = Math.min(
          TOTAL_FRAMES - 1,
          Math.max(0, Math.floor(scrollData.current.current * (TOTAL_FRAMES - 1)))
        );
        
        ctx.canvas.width = window.innerWidth;
        ctx.canvas.height = window.innerHeight;
        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = "high";
        ctx.drawImage(images[frameIndex], 0, 0, ctx.canvas.width, ctx.canvas.height);
      }
    }

    rafRef.current = requestAnimationFrame(updateCanvas);
  }, [images]);

  // Sync scroll tracker efficiently inside an event listener
  useEffect(() => {
    const onScroll = () => {
      const container = containerRef.current;
      if (!container) return;

      const rect = container.getBoundingClientRect();
      const scrollable = container.scrollHeight - window.innerHeight;
      const scrolled = -rect.top;
      
      const progress = Math.max(0, Math.min(1, scrolled / scrollable));
      scrollData.current.target = progress;
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    // start the loop
    rafRef.current = requestAnimationFrame(updateCanvas);

    return () => {
      window.removeEventListener("scroll", onScroll);
      cancelAnimationFrame(rafRef.current);
    };
  }, [updateCanvas]);

  return (
    <div
      ref={containerRef}
      style={{ height: "500vh" }}
      className="relative"
    >
      <div 
        className="sticky top-0 h-screen w-full overflow-hidden bg-black flex items-center justify-center pointer-events-none"
        style={{ willChange: "transform" }}
      >
        <canvas
          ref={canvasRef}
          className="h-full w-full object-cover"
        />
      </div>
    </div>
  );
};

export default ScrollVideo;
