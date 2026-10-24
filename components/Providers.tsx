'use client';

import type { ReactNode } from 'react';
import { MotionConfig } from 'motion/react';
import { StoreProvider } from '@/lib/store-context';

export default function Providers({ children }: { children: ReactNode }) {
  return (
    <MotionConfig reducedMotion="user" transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}>
      <StoreProvider>{children}</StoreProvider>
    </MotionConfig>
  );
}
