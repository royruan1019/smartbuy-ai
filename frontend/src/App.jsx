import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar       from './components/Navbar';
import Home         from './pages/Home';
import PriceSearch  from './pages/PriceSearch';
import ReportPrice  from './pages/ReportPrice';
import MyBasket     from './pages/MyBasket';
import SettingsPlaceholder from './pages/SettingsPlaceholder';

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/"           element={<Home />} />
        <Route path="/search"     element={<PriceSearch />} />
        <Route path="/report"     element={<ReportPrice />} />
        <Route path="/basket"     element={<MyBasket />} />
        <Route path="/settings"   element={<SettingsPlaceholder />} />
      </Routes>
    </BrowserRouter>
  );
}
