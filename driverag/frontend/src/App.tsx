import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Chat from './pages/Chat';
import Documents from './pages/Documents';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Chat />} />
          <Route path="documents" element={<Documents />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
