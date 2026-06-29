import { redirect } from 'next/navigation';

// Root "/" redirects straight to /chat (chat page handles auth guard)
export default function RootPage() {
  redirect('/chat');
}
