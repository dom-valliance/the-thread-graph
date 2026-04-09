import type { Metadata } from 'next';
import './globals.css';
import Providers from './providers';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';

export const metadata: Metadata = {
  title: 'Valliance Graph',
  description: 'Knowledge graph visualisation for Valliance',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900">
        <Providers>
          <Sidebar />
          <div className="ml-56 flex h-screen flex-col overflow-hidden">
            <Header />
            <main className="flex flex-1 flex-col overflow-auto p-6">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
