import { useEffect, useRef, useCallback } from "react";

const clips = ["/videos/clip1.mp4", "/videos/clip2.mp4", "/videos/clip3.mp4", "/videos/clip4.mp4"];

const Index = () => {
  const currentRef = useRef<HTMLVideoElement>(null);
  const nextRef = useRef<HTMLVideoElement>(null);
  const indexRef = useRef(0);

  const preloadNext = useCallback(() => {
    const nextIdx = (indexRef.current + 1) % clips.length;
    const next = nextRef.current;
    if (next) {
      next.src = clips[nextIdx];
      next.load();
    }
  }, []);

  const swapAndPlay = useCallback(() => {
    indexRef.current = (indexRef.current + 1) % clips.length;

    // Swap refs visually: hide current, show next
    const current = currentRef.current!;
    const next = nextRef.current!;

    next.style.zIndex = "2";
    current.style.zIndex = "1";
    next.play().catch(() => {});

    // Once next is playing, reload current with the NEXT next clip
    const futureIdx = (indexRef.current + 1) % clips.length;
    current.src = clips[futureIdx];
    current.load();

    // Swap refs
    const tmp = currentRef.current;
    currentRef.current = nextRef.current;
    nextRef.current = tmp;
  }, []);

  useEffect(() => {
    const a = currentRef.current!;
    const b = nextRef.current!;

    a.src = clips[0];
    a.load();
    a.style.zIndex = "2";
    b.style.zIndex = "1";
    a.play().catch(() => {});

    // Preload second clip
    b.src = clips[1];
    b.load();

    const onEndedA = () => swapAndPlay();
    const onEndedB = () => swapAndPlay();

    a.addEventListener("ended", onEndedA);
    b.addEventListener("ended", onEndedB);

    return () => {
      a.removeEventListener("ended", onEndedA);
      b.removeEventListener("ended", onEndedB);
    };
  }, [swapAndPlay]);

  const videoStyle: React.CSSProperties = {
    position: "absolute",
    top: 0,
    left: 0,
    width: "100vw",
    height: "100vh",
    objectFit: "cover",
  };

  return (
    <div style={{ position: "fixed", inset: 0, background: "#000", overflow: "hidden" }}>
      <video ref={currentRef} style={videoStyle} muted playsInline />
      <video ref={nextRef} style={videoStyle} muted playsInline />
    </div>
  );
};

export default Index;
