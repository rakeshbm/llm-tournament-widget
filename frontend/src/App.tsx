import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  HomePage,
  TournamentsPage,
  CreateTournamentPage,
  TournamentPage,
} from './pages';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useMemo } from 'react';

export default function App() {
  // TODO: Separate the query client and import here
  const queryClient = useMemo(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // 5 minutes
            gcTime: 10 * 60 * 1000, // 10 minutes
            retry: 1,
            refetchOnWindowFocus: false,
          },
          mutations: {
            retry: 0,
          },
        },
      }),
    []
  );

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/home" element={<HomePage />} />
          <Route path="/tournaments" element={<TournamentsPage />} />
          <Route
            path="/tournaments/create"
            element={<CreateTournamentPage />}
          />
          <Route path="/tournaments/:id" element={<TournamentPage />} />
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="*" element={<Navigate to="/home" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
