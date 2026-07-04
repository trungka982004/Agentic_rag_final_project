'use client';

import { useState, useEffect, useCallback } from 'react';
import { apiGetMe } from '@/services/api';
import type { User } from '@/types';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchMe = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) { setLoading(false); return; }
    try {
      const me = await apiGetMe();
      setUser(me);
    } catch {
      localStorage.removeItem('access_token');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchMe(); }, [fetchMe]);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    setUser(null);
    window.location.href = '/login';
  }, []);

  return { user, loading, logout, refetch: fetchMe };
}
