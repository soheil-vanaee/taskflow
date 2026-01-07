'use client';

import { AuthProvider as AuthProviderImpl } from '@/contexts/AuthContext';
import { ReactNode } from 'react';

export function AuthProvider({ children }: { children: ReactNode }) {
  return (
    <AuthProviderImpl>
      {children}
    </AuthProviderImpl>
  );
}