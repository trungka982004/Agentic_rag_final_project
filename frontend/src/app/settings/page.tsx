'use client';

// Settings home = General Setting (Cấu hình chung) — redirects to /settings/config as default
import { redirect } from 'next/navigation';

export default function SettingsPage() {
  redirect('/settings/config');
}
