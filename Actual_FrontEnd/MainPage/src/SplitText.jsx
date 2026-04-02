import { useRef, useEffect, useState } from 'react';
import { gsap } from 'gsap';
import { SplitText as GSAPSplitText } from 'gsap/SplitText';
import { useGSAP } from '@gsap/react';

gsap.registerPlugin(GSAPSplitText, useGSAP);

const SplitText = ({
  text,
  className = '',
  delay = 50,
  duration = 1.25,
  ease = 'power3.out',
  splitType = 'chars',
  from = { opacity: 0, y: 40 },
  to = { opacity: 1, y: 0 },
  textAlign = 'center',
  tag = 'p',
  onLetterAnimationComplete
}) => {
  const ref = useRef(null);
  const animationCompletedRef = useRef(false);
  const [fontsLoaded, setFontsLoaded] = useState(false);

  useEffect(() => {
    if (document.fonts.status === 'loaded') {
      setFontsLoaded(true);
    } else {
      document.fonts.ready.then(() => setFontsLoaded(true));
    }
  }, []);

  useGSAP(
    () => {
      if (!ref.current || !text || !fontsLoaded) return;
      if (animationCompletedRef.current) return;

      const el = ref.current;

      // Reveal the parent container now that fonts are loaded and GSAP is ready
      gsap.set(el, { opacity: 1 });

      const splitInstance = new GSAPSplitText(el, {
        type: splitType,
        smartWrap: true,
        autoSplit: splitType === 'lines',
        linesClass: 'split-line',
        wordsClass: 'split-word',
        charsClass: 'split-char',
        reduceWhiteSpace: false,
      });

      let targets;
      if (splitType.includes('chars') && splitInstance.chars.length) targets = splitInstance.chars;
      else if (splitType.includes('words') && splitInstance.words.length) targets = splitInstance.words;
      else if (splitType.includes('lines') && splitInstance.lines.length) targets = splitInstance.lines;
      else targets = splitInstance.chars || splitInstance.words || splitInstance.lines;

      gsap.fromTo(
        targets,
        { ...from },
        {
          ...to,
          duration,
          ease,
          stagger: delay / 1000,
          onComplete: () => {
            animationCompletedRef.current = true;
            if (onLetterAnimationComplete) onLetterAnimationComplete();
          },
          willChange: 'transform, opacity',
          force3D: true
        }
      );

      return () => {
        // We only revert the split instance, leaving the DOM clean if unmounted
        if (splitInstance) {
          try {
            splitInstance.revert();
          } catch (_) { /* noop */ }
        }
      };
    },
    {
      dependencies: [text, delay, duration, ease, splitType, JSON.stringify(from), JSON.stringify(to), fontsLoaded],
      scope: ref
    }
  );

  const renderTag = () => {
    const style = {
      textAlign,
      overflow: 'hidden',
      display: 'inline-block',
      whiteSpace: 'normal',
      wordWrap: 'break-word',
      willChange: 'transform, opacity',
      opacity: 0 // Prevent FOUC before GSAP runs
    };
    const Tag = tag || 'p';

    return (
      <Tag ref={ref} style={style} className={`split-parent ${className}`}>
        {text}
      </Tag>
    );
  };
  return renderTag();
};

export default SplitText;

