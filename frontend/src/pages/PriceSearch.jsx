import { useState, useEffect } from 'react';
import { useApi, get } from '../hooks/useApi';

const CATEGORY_CHIPS = ['全部', '葉菜', '瓜果', '根莖', '豆類'];
const FEATURED_COUNT = 20;
const STATUS_RANK = { '便宜': 0, '正常': 1, '偏貴': 2, '資料不足': 3 };

const STATUS_BADGE = {
  '便宜': 'yz-bdg-g',
  '正常': 'yz-bdg-gr',
  '偏貴': 'yz-bdg-o',
  '資料不足': 'yz-bdg-gr',
};

const STATUS_ARROW = {
  '便宜': { arrow: '↓', color: '#16A34A' },
  '偏貴': { arrow: '↑', color: '#DC2626' },
  '正常': { arrow: '→', color: '#888' },
  '資料不足': { arrow: '·', color: '#9B9A90' },
};

const labelStyle = { fontSize: 10, fontWeight: 700, color: 'var(--yz-dim)', letterSpacing: '.08em', textTransform: 'uppercase', marginBottom: 7 };
const metricLabel = { fontSize: 11, fontWeight: 600, color: 'var(--yz-mut)', marginBottom: 7 };

// 24節氣推薦食材沿用早期示範資料的命名，跟批發市場真實品名（crop_name）用詞不同，
// 例如「高麗菜」在真實資料叫「甘藍」、「冬瓜」沒有單一品項只有「冬瓜-其他」等細分品種。
// 這裡做別名對照，讓點擊後能找到對應的真實品項。
const PRODUCT_ALIASES = {
  '高麗菜': '甘藍',
  '空心菜': '蕹菜',
  '四季豆': '菜豆',
  '地瓜': '甘薯',
  '地瓜葉': '甘薯葉',
  '白蘿蔔': '蘿蔔',
  '青江菜': '青江白菜',
};

function DemoChart() {
  return (
    <svg viewBox="0 0 650 148" width="100%" height="148" style={{ overflow: 'visible' }}>
      <defs>
        <linearGradient id="yz-ga" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#1D9E75" stopOpacity="0.12" />
          <stop offset="100%" stopColor="#1D9E75" stopOpacity="0" />
        </linearGradient>
      </defs>
      <line x1="30" y1="18" x2="620" y2="18" stroke="#E2DDD2" strokeWidth="1" />
      <line x1="30" y1="52" x2="620" y2="52" stroke="#E2DDD2" strokeWidth="1" />
      <line x1="30" y1="86" x2="620" y2="86" stroke="#E2DDD2" strokeWidth="1" />
      <line x1="30" y1="120" x2="620" y2="120" stroke="#E2DDD2" strokeWidth="1" />
      <path d="M30,55 L75,48 L120,40 L165,52 L210,38 L255,34 L300,44 L345,50 L390,58 L435,52 L480,64 L525,72 L570,78 L570,120 L30,120Z" fill="url(#yz-ga)" />
      <path d="M30,55 L75,48 L120,40 L165,52 L210,38 L255,34 L300,44 L345,50 L390,58 L435,52 L480,64 L525,72 L570,78" stroke="#1D9E75" strokeWidth="2.5" fill="none" strokeLinejoin="round" strokeLinecap="round" />
      <circle cx="570" cy="78" r="4.5" fill="white" stroke="#1D9E75" strokeWidth="2.5" />
      <text x="24" y="135" fontSize="9" fill="#9B9A90">30天前</text>
      <text x="554" y="135" fontSize="9" fill="#1D9E75" fontWeight="bold">今日</text>
    </svg>
  );
}

function AuctionDetailModal({ detail, onClose }) {
  const d = detail.price_detail || {};
  const rows = [
    ['交易日期', d.trans_date || '—'],
    ['批發市場', d.market_name || '—'],
    ['上價', d.upper_price != null ? `${d.upper_price} 元/kg` : '—'],
    ['中價（今日均價）', d.middle_price != null ? `${d.middle_price} 元/kg` : '—'],
    ['下價', d.lower_price != null ? `${d.lower_price} 元/kg` : '—'],
    ['交易量', d.volume != null ? `${d.volume} 公斤` : '—'],
  ];
  return (
    <div
      onClick={onClose}
      style={{ position: 'fixed', inset: 0, background: 'rgba(26,26,24,.45)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}
    >
      <div onClick={e => e.stopPropagation()} className="yz-card" style={{ width: 360, padding: '24px 26px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700 }}>{detail.product_name} · 拍賣行情明細</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 18, color: 'var(--yz-dim)' }}>✕</button>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {rows.map(([label, value]) => (
            <div key={label} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, paddingBottom: 8, borderBottom: '1px solid #F0ECE5' }}>
              <span style={{ color: 'var(--yz-mut)' }}>{label}</span>
              <span style={{ fontWeight: 600 }}>{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function PriceListPanel({ jumpToProduct, onJumpHandled }) {
  const [query, setQuery] = useState('');
  const [markets, setMarkets] = useState([]);
  const [market, setMarket] = useState('');
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAll, setShowAll] = useState(false);
  const [selectedName, setSelectedName] = useState(null);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [trendExpanded, setTrendExpanded] = useState(false);
  const [auctionModalOpen, setAuctionModalOpen] = useState(false);

  useEffect(() => {
    get('/api/markets').then(d => setMarkets(d.markets || [])).catch(() => setMarkets([]));
  }, []);

  async function doSearch(q, m, autoSelect = true) {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (q) params.set('q', q);
      if (m) params.set('market', m);
      const data = await get(`/api/products?${params.toString()}`);
      setItems(data);
      if (data.length && autoSelect) openDetail(data[0].product_name, m);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  // 掛載當下若已有待跳轉的品項（從 24節氣頁籤點過來），就不要讓預設清單搶著選第一筆，避免兩個請求互相覆蓋。
  useEffect(() => { doSearch('', '', !jumpToProduct); }, []); // eslint-disable-line

  async function openDetail(name, m = market) {
    setSelectedName(name);
    setDetailLoading(true);
    setTrendExpanded(false);
    setAuctionModalOpen(false);
    try {
      const params = m ? `?market=${encodeURIComponent(m)}` : '';
      const d = await get(`/api/products/${encodeURIComponent(name)}${params}`);
      setDetail(d);
    } catch {
      setDetail(null);
    } finally {
      setDetailLoading(false);
    }
  }

  async function resolveAndJump(name) {
    // 24節氣的推薦食材名稱可能跟真實品項用詞不同，改用搜尋＋別名比對找出最接近的真實品項
    const term = PRODUCT_ALIASES[name] || name;
    try {
      const matches = await get(`/api/products?q=${encodeURIComponent(term)}`);
      if (matches.length) {
        openDetail(matches[0].product_name);
        return;
      }
    } catch { /* fall through to not-found state below */ }
    setSelectedName(name);
    setDetail(null);
  }

  useEffect(() => {
    if (jumpToProduct) {
      setQuery('');
      setShowAll(false);
      resolveAndJump(jumpToProduct);
      onJumpHandled();
    }
  }, [jumpToProduct]); // eslint-disable-line

  function handleSearchSubmit(e) {
    e.preventDefault();
    setShowAll(false);
    doSearch(query, market);
  }

  function handleMarketChange(e) {
    const m = e.target.value;
    setMarket(m);
    setShowAll(false);
    doSearch(query, m);
  }

  const isFiltering = query.trim() !== '';
  const visibleItems = isFiltering || showAll
    ? items
    : [...items].sort((a, b) => (STATUS_RANK[a.status] ?? 9) - (STATUS_RANK[b.status] ?? 9)).slice(0, FEATURED_COUNT);

  return (
    <div style={{ display: 'flex', minHeight: 600, border: '1px solid var(--yz-bdr)', borderRadius: 12, overflow: 'hidden', background: '#fff' }}>
      {/* Left sidebar */}
      <div style={{ width: 256, flexShrink: 0, borderRight: '1px solid var(--yz-bdr)', display: 'flex', flexDirection: 'column' }}>
        <form onSubmit={handleSearchSubmit} style={{ padding: '14px 14px 10px' }}>
          <input className="yz-input" placeholder="搜尋品項..." value={query} onChange={e => setQuery(e.target.value)} />
        </form>
        <div style={{ padding: '0 14px 10px' }}>
          <p style={labelStyle}>批發市場</p>
          <select className="yz-input" value={market} onChange={handleMarketChange} style={{ fontSize: 13 }}>
            <option value="">全部市場</option>
            {markets.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>
        <div style={{ padding: '0 14px 12px' }}>
          <p style={labelStyle}>蔬菜種類</p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
            {CATEGORY_CHIPS.map((c, i) => (
              <span
                key={c}
                title={i === 0 ? undefined : '分類篩選功能開發中'}
                style={{
                  padding: '4px 10px', borderRadius: 6, fontSize: 11, fontWeight: 600,
                  background: i === 0 ? 'var(--yz-g)' : '#F7F4EF',
                  color: i === 0 ? '#fff' : 'var(--yz-mut)',
                  border: i === 0 ? 'none' : '1px solid var(--yz-bdr)',
                  cursor: i === 0 ? 'default' : 'not-allowed',
                  opacity: i === 0 ? 1 : .55,
                }}
              >{c}</span>
            ))}
          </div>
        </div>
        <div style={{ height: 1, background: 'var(--yz-bdr)' }} />
        <div style={{ flex: 1, overflowY: 'auto' }}>
          {!isFiltering && (
            <p style={{ padding: '10px 14px 2px', fontSize: 10, fontWeight: 700, color: 'var(--yz-dim)', letterSpacing: '.07em', textTransform: 'uppercase' }}>
              {showAll ? `全部品項（${items.length}）` : '精選品項'}
            </p>
          )}
          {loading && <p style={{ padding: 14, fontSize: 12, color: 'var(--yz-dim)' }}>載入中...</p>}
          {!loading && items.length === 0 && <p style={{ padding: 14, fontSize: 12, color: 'var(--yz-dim)' }}>查無品項，請先啟動 API 伺服器或換個關鍵字</p>}
          {visibleItems.map(item => {
            const active = item.product_name === selectedName;
            const { arrow, color } = STATUS_ARROW[item.status] || STATUS_ARROW['資料不足'];
            return (
              <div
                key={item.product_name}
                onClick={() => openDetail(item.product_name)}
                style={{
                  padding: '10px 14px', cursor: 'pointer', borderBottom: '1px solid #F0ECE5',
                  background: active ? 'var(--yz-gl)' : 'transparent',
                  borderLeft: active ? '3px solid var(--yz-g)' : '3px solid transparent',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 2 }}>
                  <span style={{ fontSize: active ? 14 : 13, fontWeight: active ? 700 : 400, color: active ? 'var(--yz-gd)' : 'var(--yz-txt)' }}>{item.product_name}</span>
                  <span style={{ fontSize: 11, fontWeight: 600, color }}>{arrow} {item.status}</span>
                </div>
                <span style={{ fontSize: active ? 16 : 13, fontWeight: 700, color: active ? 'var(--yz-g)' : 'var(--yz-txt)' }}>
                  {item.today_price != null ? `${item.today_price} 元/kg` : '暫無報價'}
                </span>
              </div>
            );
          })}
          {!isFiltering && !loading && items.length > FEATURED_COUNT && (
            <button
              onClick={() => setShowAll(v => !v)}
              style={{ width: '100%', padding: '10px 14px', background: 'none', border: 'none', borderTop: '1px solid var(--yz-bdr)', color: 'var(--yz-g)', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}
            >
              {showAll ? '▴ 收合' : `顯示全部 ${items.length} 項 ▾`}
            </button>
          )}
        </div>
      </div>

      {/* Right detail panel */}
      <div style={{ flex: 1, padding: '28px 32px', overflowY: 'auto' }}>
        {!selectedName && <p style={{ color: 'var(--yz-dim)', fontSize: 14 }}>請從左側選擇品項查看詳情</p>}
        {selectedName && detailLoading && <p style={{ color: 'var(--yz-dim)', fontSize: 14 }}>載入中...</p>}
        {selectedName && !detailLoading && !detail && <p style={{ color: 'var(--yz-dim)', fontSize: 14 }}>無法取得詳細資料</p>}
        {selectedName && !detailLoading && detail && (
          <>
            <div style={{ marginBottom: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 5 }}>
                <h2 style={{ fontSize: 24, fontWeight: 900 }}>{detail.product_name}</h2>
                <span className={`yz-bdg ${STATUS_BADGE[detail.price_status] || 'yz-bdg-gr'}`}>{detail.price_status}</span>
              </div>
              <p style={{ fontSize: 12, color: 'var(--yz-mut)' }}>
                {detail.price_detail?.market_name ? `${detail.price_detail.market_name} · ` : ''}近 30 天資料
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 14, marginBottom: 22 }}>
              <div
                className="yz-card"
                style={{ padding: '16px 20px', cursor: 'pointer' }}
                onClick={() => setAuctionModalOpen(true)}
                title="點擊查看完整拍賣行情明細"
              >
                <p style={metricLabel}>今日均價</p>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 5 }}>
                  <span style={{ fontSize: 30, fontWeight: 900 }}>{detail.today_price ?? '—'}</span>
                  <span style={{ fontSize: 13, color: 'var(--yz-mut)' }}>元/kg</span>
                </div>
                <p style={{ fontSize: 11, color: 'var(--yz-g)', fontWeight: 600, marginTop: 6 }}>查看明細 →</p>
              </div>
              <div className="yz-card" style={{ padding: '16px 20px' }}>
                <p style={metricLabel}>30 天均價</p>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 5 }}>
                  <span style={{ fontSize: 30, fontWeight: 900 }}>{detail.price_detail?.recent_average ?? '—'}</span>
                  <span style={{ fontSize: 13, color: 'var(--yz-mut)' }}>元/kg</span>
                </div>
              </div>
              <div className="yz-card" style={{ padding: '16px 20px' }}>
                <p style={metricLabel}>採買建議</p>
                <p style={{ fontSize: 15, fontWeight: 700, color: 'var(--yz-g)' }}>{detail.recommendation}</p>
              </div>
            </div>

            <div className="yz-card" style={{ padding: '20px 24px', marginBottom: 16 }}>
              <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 14 }}>{detail.product_name} · 30 天走勢</h4>
              <DemoChart />
              <p style={{ fontSize: 11, color: 'var(--yz-dim)', marginTop: 8 }}>⚠ 示範圖表，串接每日歷史價格 API 後將顯示真實走勢</p>
            </div>

            <div className="yz-card" style={{ padding: '13px 20px', marginBottom: 16, cursor: 'pointer' }} onClick={() => setTrendExpanded(v => !v)}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span>{detail.price_status === '便宜' ? '📉' : detail.price_status === '偏貴' ? '📈' : '📊'}</span>
                  <span style={{ fontSize: 13 }}>{detail.price_detail?.reason}</span>
                </div>
                <span style={{ fontSize: 12, color: 'var(--yz-g)', fontWeight: 600 }}>{trendExpanded ? '▴ 收合' : '▾ 展開詳細說明'}</span>
              </div>
              {trendExpanded && (
                <p style={{ marginTop: 10, fontSize: 13, color: 'var(--yz-mut)', lineHeight: 1.65 }}>
                  {detail.advice} {detail.price_detail?.suggestion}
                </p>
              )}
            </div>

            <div style={{ border: '1.5px dashed #B8B0E8', borderRadius: 12, padding: '20px 24px', background: '#FAFAFE' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <span>✦</span>
                <h4 style={{ fontSize: 14, fontWeight: 700, color: 'var(--yz-pu)' }}>AI 價格預測</h4>
                <span className="yz-bdg yz-bdg-p">模型開發中</span>
              </div>
              <p style={{ fontSize: 12, color: 'var(--yz-mut)', lineHeight: 1.65 }}>
                AI 預測模型尚在訓練中，上線後將提供未來 7 天逐日預測均價與短中期研判摘要。
              </p>
            </div>
          </>
        )}
      </div>

      {auctionModalOpen && detail && (
        <AuctionDetailModal detail={detail} onClose={() => setAuctionModalOpen(false)} />
      )}
    </div>
  );
}

function getNextTermCountdown(terms) {
  if (!terms?.length) return null;
  const today = new Date();
  const todayMidnight = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  const todayKey = (today.getMonth() + 1) * 100 + today.getDate();
  const sorted = [...terms].sort((a, b) => (a.start_month * 100 + a.start_day) - (b.start_month * 100 + b.start_day));
  let next = sorted.find(t => (t.start_month * 100 + t.start_day) > todayKey);
  let year = today.getFullYear();
  if (!next) { next = sorted[0]; year += 1; }
  const nextDate = new Date(year, next.start_month - 1, next.start_day);
  const days = Math.round((nextDate - todayMidnight) / 86400000);
  return { name: next.term_name, days };
}

function ProductBadge({ name, onJump }) {
  return (
    <button
      onClick={() => onJump(name)}
      className="yz-bdg yz-bdg-g"
      style={{ border: 'none', cursor: 'pointer' }}
      title={`查看「${name}」真實行情`}
    >{name}</button>
  );
}

function SolarTermPanel({ onJumpToProduct }) {
  const seasonEmoji = { 春: '🌸', 夏: '☀️', 秋: '🍂', 冬: '❄️' };
  const today = useApi('/api/solar-term');
  const all = useApi('/api/solar-term/all');
  const countdown = getNextTermCountdown(all.data);

  return (
    <div>
      {today.loading && <p style={{ color: 'var(--yz-dim)', fontSize: 14 }}>載入中...</p>}
      {today.data && (
        <div className="yz-card" style={{ padding: '24px 28px', marginBottom: 28 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <span style={{ fontSize: 38 }}>{seasonEmoji[today.data.season] || '🌿'}</span>
              <div>
                <p style={{ fontSize: 12, color: 'var(--yz-mut)', marginBottom: 2 }}>現在節氣</p>
                <h2 style={{ fontSize: 20, fontWeight: 900 }}>{today.data.term_name}</h2>
                <span className="yz-bdg yz-bdg-g" style={{ marginTop: 4, display: 'inline-block' }}>{today.data.season}季</span>
              </div>
            </div>
            {countdown && (
              <div style={{ textAlign: 'right' }}>
                <p style={{ fontSize: 11, color: 'var(--yz-mut)', marginBottom: 2 }}>距離下一個節氣</p>
                <p style={{ fontSize: 14, fontWeight: 700, color: 'var(--yz-g)' }}>「{countdown.name}」還有 {countdown.days} 天</p>
              </div>
            )}
          </div>
          <p style={{ fontSize: 13, color: 'var(--yz-mut)', lineHeight: 1.7, marginBottom: 12 }}>{today.data.description}</p>
          {today.data.shopping_tip && <p style={{ fontSize: 13, marginBottom: 6 }}>🛒 {today.data.shopping_tip}</p>}
          {today.data.health_tip && <p style={{ fontSize: 13, marginBottom: 6 }}>💚 {today.data.health_tip}</p>}
          {today.data.risk_note && (
            <p style={{ fontSize: 13, color: 'var(--yz-or)', background: 'var(--yz-orl)', borderRadius: 8, padding: '8px 12px', marginTop: 8 }}>⚠️ {today.data.risk_note}</p>
          )}
          {today.data.recommended_products?.length > 0 && (
            <div style={{ marginTop: 14, paddingTop: 14, borderTop: '1px solid var(--yz-bdr)' }}>
              <p style={{ fontSize: 11, color: 'var(--yz-mut)', marginBottom: 8 }}>本節氣推薦食材（點擊查看真實行情）</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {today.data.recommended_products.map(p => <ProductBadge key={p} name={p} onJump={onJumpToProduct} />)}
              </div>
            </div>
          )}
        </div>
      )}

      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 14, paddingLeft: 12, borderLeft: '4px solid var(--yz-g)' }}>全年節氣一覽</h3>
      {all.loading && <p style={{ color: 'var(--yz-dim)', fontSize: 14 }}>載入中...</p>}
      {all.data && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(220px,1fr))', gap: 14 }}>
          {all.data.map((term, i) => {
            const isCurrent = today.data?.term_name === term.term_name;
            const products = String(term.common_products || '').split(';').filter(Boolean);
            return (
              <div key={i} className="yz-card" style={{ padding: '16px 18px', border: isCurrent ? '2px solid var(--yz-g)' : undefined }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                  <span style={{ fontSize: 24 }}>{seasonEmoji[term.season] || '🌿'}</span>
                  <div>
                    <p style={{ fontSize: 14, fontWeight: 700 }}>{term.term_name}</p>
                    <p style={{ fontSize: 11, color: 'var(--yz-mut)' }}>{term.season}季</p>
                  </div>
                  {isCurrent && <span className="yz-bdg yz-bdg-g" style={{ marginLeft: 'auto' }}>現在</span>}
                </div>
                <p style={{ fontSize: 12.5, color: 'var(--yz-mut)', lineHeight: 1.55, marginBottom: 8 }}>{term.description}</p>
                {products.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                    {products.map(p => <ProductBadge key={p} name={p} onJump={onJumpToProduct} />)}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function PriceSearch() {
  const [tab, setTab] = useState('prices');
  const [jumpToProduct, setJumpToProduct] = useState(null);

  function handleJumpToProduct(name) {
    setTab('prices');
    setJumpToProduct(name);
  }

  return (
    <div className="yz-page" style={{ padding: '28px 40px 56px' }}>
      <div style={{ maxWidth: 1280, margin: '0 auto' }}>
        <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
          <button className={`yz-btn yz-btn-sm ${tab === 'prices' ? 'yz-btn-g' : 'yz-btn-gho'}`} onClick={() => setTab('prices')}>品項行情</button>
          <button className={`yz-btn yz-btn-sm ${tab === 'solar' ? 'yz-btn-g' : 'yz-btn-gho'}`} onClick={() => setTab('solar')}>24節氣指南</button>
        </div>
        {tab === 'prices'
          ? <PriceListPanel jumpToProduct={jumpToProduct} onJumpHandled={() => setJumpToProduct(null)} />
          : <SolarTermPanel onJumpToProduct={handleJumpToProduct} />}
      </div>
    </div>
  );
}
