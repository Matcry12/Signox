import React, { useState } from 'react';
import { 
  Menu, 
  User, 
  Search, 
  BookOpen, 
  MessageSquare, 
  Trophy, 
  Play, 
  ChevronRight, 
  MoreHorizontal, 
  Heart, 
  Share2, 
  ChevronDown,
  Volume2,
  Bookmark,
  Flag,
  Info,
  ArrowRight,
  ArrowLeft
} from 'lucide-react';

/**
 * MOCK DATA
 */
const MOCK_TOPICS = [
  { id: 1, title: 'Gia đình', color: 'bg-red-400' },
  { id: 2, title: 'Trường học', color: 'bg-orange-400' },
  { id: 3, title: 'Bệnh viện', color: 'bg-yellow-400' },
  { id: 4, title: 'Giao thông', color: 'bg-green-400' },
  { id: 5, title: 'Cảm xúc', color: 'bg-blue-400' },
];

const FORUM_POSTS = [
  { id: 1, user: 'USER #1', date: '12/12/2023', title: 'Lịch sử Ngôn ngữ ký hiệu', content: 'Tìm hiểu về nguồn gốc và sự phát triển...', type: 'article', likes: 45, comments: 12 },
  { id: 2, user: 'HANG USER', date: '11/12/2023', title: 'Hỏi về từ vựng "Máy tính"', content: 'Có ai biết ký hiệu cho từ này không ạ?', type: 'discussion', likes: 8, comments: 2 },
];

/**
 * REUSABLE COMPONENTS
 */

const Card = ({ children, className = "" }) => (
  <div className={`bg-white rounded-2xl shadow-sm p-4 ${className}`}>
    {children}
  </div>
);

const SectionTitle = ({ title, subtitle }) => (
  <div className="mb-4 text-center">
    <h3 className="text-slate-700 font-bold text-lg uppercase tracking-wide">
      {title}
    </h3>
    {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
  </div>
);

// New component for the "Book Shelf" effect described in Docx Item 6
const BookItem = ({ title, color }) => (
  <div className="group relative w-16 h-48 cursor-pointer transition-all duration-300 ease-out hover:-translate-y-4 mx-1">
    {/* Book Spine */}
    <div className={`absolute inset-0 ${color} rounded-l-md shadow-md border-r border-white/20 flex items-center justify-center writing-vertical-lr`}>
      <span className="transform rotate-180 text-white font-bold text-sm tracking-wider whitespace-nowrap py-4">
        {title}
      </span>
    </div>
    {/* Book Side/Paper effect */}
    <div className="absolute top-1 bottom-1 right-0 w-2 bg-white/90 rounded-r-sm"></div>
  </div>
);

/**
 * VIEW: HOME (TRANG CHỦ)
 */
const HomeView = ({ onNavigate }) => {
  return (
    <div className="space-y-8 pb-24">
      {/* 1. Updated Hero Section - "Rhythm of Signs" */}
      <div className="relative h-64 overflow-hidden rounded-b-[2.5rem] shadow-lg group">
        {/* Background Image Placeholder with Scenic Vibe */}
        <div className="absolute inset-0 bg-gradient-to-br from-teal-800 to-slate-900">
          <div className="absolute inset-0 opacity-40 bg-[url('https://images.unsplash.com/photo-1501785888041-af3ef285b470?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80')] bg-cover bg-center mix-blend-overlay"></div>
        </div>
        
        {/* Header Overlay */}
        <div className="absolute top-0 left-0 right-0 p-4 flex justify-between items-center z-20">
          <div className="bg-white/20 backdrop-blur-md p-2 rounded-full text-white"><Menu size={20} /></div>
          <div className="bg-white/20 backdrop-blur-md p-2 rounded-full text-white"><User size={20} /></div>
        </div>

        {/* Hero Text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center z-10 px-6 pt-8">
          <h1 className="font-serif text-4xl text-white tracking-wider mb-2 drop-shadow-lg opacity-0 animate-fade-in-up" style={{animationDelay: '0.1s', animationFillMode: 'forwards'}}>
            Rhythm of Signs
          </h1>
          <p className="text-teal-100 text-sm font-light tracking-[0.2em] uppercase opacity-0 animate-fade-in-up" style={{animationDelay: '0.3s', animationFillMode: 'forwards'}}>
            Study and share together
          </p>
        </div>
      </div>

      {/* 2. SIGN LEARNING Navigation (Danh mục) */}
      <div className="px-6 -mt-4 relative z-20">
        <div className="bg-white rounded-3xl shadow-lg p-6">
          <SectionTitle title="SIGN LEARNING" />
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Diễn đàn', icon: MessageSquare, id: 'forum', color: 'text-blue-500 bg-blue-50' },
              { label: 'Thư viện', icon: BookOpen, id: 'library', color: 'text-teal-500 bg-teal-50' },
              { label: 'Chủ đề', icon: Bookmark, id: 'practice', color: 'text-purple-500 bg-purple-50' },
              { label: 'Về chúng tôi', icon: Info, id: 'about', color: 'text-orange-500 bg-orange-50' }
            ].map((item) => (
              <div 
                key={item.id} 
                onClick={() => onNavigate(item.id)}
                className="flex flex-col items-center gap-3 cursor-pointer group"
              >
                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-transform group-hover:scale-110 ${item.color}`}>
                  <item.icon size={20} />
                </div>
                <span className="text-[10px] font-bold text-slate-500 text-center leading-tight">{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 6. Book Shelf / Topics (Mục bài học) */}
      <div className="px-0 mt-8">
        <div className="px-6 mb-4 flex justify-between items-end">
          <SectionTitle title="Bài học theo chủ đề" />
        </div>
        {/* Book Shelf Container */}
        <div className="relative bg-[#f0e6d2] py-8 border-y-8 border-[#d4c5a9] shadow-inner overflow-hidden">
             {/* Shelf Shadow */}
             <div className="absolute top-0 left-0 w-full h-4 bg-gradient-to-b from-black/10 to-transparent pointer-events-none"></div>
             
             <div className="flex justify-center items-end px-4 gap-1 overflow-x-auto no-scrollbar pb-2">
                {MOCK_TOPICS.map((topic) => (
                  <BookItem key={topic.id} title={topic.title} color={topic.color} />
                ))}
             </div>
             
             {/* Wooden Shelf Edge */}
             <div className="absolute bottom-0 left-0 w-full h-3 bg-[#a39073]"></div>
        </div>
        <p className="text-center text-xs text-gray-400 mt-2 italic">Di chuột vào sách để chọn</p>
      </div>

      {/* 7. Common Sentences (Mẫu câu thông dụng) */}
      <div className="px-6">
         <SectionTitle title="Mẫu câu thông dụng" subtitle="Trong đời sống hàng ngày" />
         
         <div className="flex gap-4 overflow-x-auto pb-6 pt-2 snap-x">
            {[
              { title: 'Giao tiếp Hàng Ngày', color: 'from-blue-400 to-blue-600' },
              { title: 'Giao tiếp Trường Học', color: 'from-teal-400 to-teal-600' },
              { title: 'Giao tiếp Công Việc', color: 'from-indigo-400 to-indigo-600' }
            ].map((card, i) => (
              <div key={i} className={`snap-center min-w-[240px] h-32 rounded-xl bg-gradient-to-r ${card.color} p-4 flex items-center justify-center shadow-md relative overflow-hidden group cursor-pointer`}>
                 <div className="absolute right-0 bottom-0 opacity-20 transform translate-x-4 translate-y-4">
                    <MessageSquare size={80} color="white" />
                 </div>
                 <h4 className="text-white font-bold text-lg text-center z-10">{card.title}</h4>
              </div>
            ))}
         </div>
      </div>
    </div>
  );
};

/**
 * VIEW: LIBRARY (THƯ VIỆN)
 * Updated based on Docx Item 4 & 5
 */
const LibraryView = () => {
  return (
    <div className="space-y-6 pb-24 px-4 pt-4">
      <SectionTitle title="LIBRARY" />
      
      {/* 4. Search Bar */}
      <div className="relative shadow-sm">
        <input 
          type="text" 
          placeholder="Tìm kiếm từ vựng..." 
          className="w-full pl-4 pr-10 py-3 rounded-full border border-gray-200 bg-white focus:outline-none focus:ring-2 focus:ring-teal-500 text-sm"
        />
        <div className="absolute right-2 top-2 p-1.5 bg-teal-500 rounded-full text-white">
          <Search size={14} />
        </div>
      </div>

      {/* 5. Search Result Detail Card */}
      <Card className="border border-slate-100 overflow-hidden !p-0">
        <div className="p-4 border-b border-slate-50 text-center">
           <h2 className="text-xl font-bold text-slate-800">Từ: <span className="text-teal-600">Xinh đẹp</span></h2>
        </div>
        
        <div className="p-4">
          <div className="flex flex-col gap-4">
            {/* Left/Top: Video + Actions */}
            <div className="w-full">
              <div className="bg-slate-200 rounded-lg h-48 flex items-center justify-center relative group overflow-hidden">
                <Play className="text-white w-12 h-12 opacity-80" fill="currentColor" />
                <div className="absolute bottom-2 right-2 bg-black/50 text-white text-[10px] px-2 py-1 rounded">00:15</div>
              </div>
              
              {/* The 3 Dots Actions (Like, Save, Report) */}
              <div className="flex justify-center gap-6 mt-4">
                <button className="flex flex-col items-center gap-1 group">
                   <div className="w-8 h-8 rounded bg-pink-50 text-pink-500 flex items-center justify-center group-hover:bg-pink-100 transition-colors">
                      <Heart size={16} />
                   </div>
                   <span className="text-[10px] text-slate-400">Like</span>
                </button>
                <button className="flex flex-col items-center gap-1 group">
                   <div className="w-8 h-8 rounded bg-blue-50 text-blue-500 flex items-center justify-center group-hover:bg-blue-100 transition-colors">
                      <Bookmark size={16} />
                   </div>
                   <span className="text-[10px] text-slate-400">Save</span>
                </button>
                <button className="flex flex-col items-center gap-1 group">
                   <div className="w-8 h-8 rounded bg-gray-50 text-gray-400 flex items-center justify-center group-hover:bg-gray-200 transition-colors">
                      <Flag size={16} />
                   </div>
                   <span className="text-[10px] text-slate-400">Report</span>
                </button>
              </div>
            </div>

            {/* Right/Bottom: Details */}
            <div className="space-y-4 bg-slate-50 p-4 rounded-xl">
              <div className="flex gap-3">
                <div className="mt-1"><div className="w-2 h-2 rounded-full bg-teal-500"></div></div>
                <div>
                  <h5 className="text-xs font-bold text-slate-400 uppercase">Miền (Region)</h5>
                  <p className="text-sm font-medium text-slate-700">Miền Bắc</p>
                </div>
              </div>

              <div className="flex gap-3">
                 <div className="mt-1"><div className="w-2 h-2 rounded-full bg-orange-500"></div></div>
                 <div>
                  <h5 className="text-xs font-bold text-slate-400 uppercase">Ý nghĩa (Meaning)</h5>
                  <p className="text-sm text-slate-600">Chỉ người/sự vật hoặc sự việc nào đó đẹp.</p>
                 </div>
              </div>

              <div className="flex gap-3">
                 <div className="mt-1"><div className="w-2 h-2 rounded-full bg-purple-500"></div></div>
                 <div>
                  <h5 className="text-xs font-bold text-slate-400 uppercase">Cách làm (How to)</h5>
                  <p className="text-sm text-slate-600">Xòe bàn tay trái hoặc phải, quét qua toàn bộ mặt rồi nắm tay lại đồng thời giơ ngón cái lên hướng về người đối diện.</p>
                 </div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Related Content */}
      <div>
        <h4 className="font-bold text-slate-700 mb-3 text-sm">Các ngôn ngữ ký hiệu cùng chủ đề</h4>
        <div className="grid grid-cols-2 gap-3">
          <div className="h-24 bg-slate-100 rounded-lg flex items-center justify-center border-2 border-dashed border-slate-200">
             <span className="text-slate-400 text-xs">Video Placeholder</span>
          </div>
          <div className="h-24 bg-slate-100 rounded-lg flex items-center justify-center border-2 border-dashed border-slate-200">
             <span className="text-slate-400 text-xs">Video Placeholder</span>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * VIEW: ABOUT US (VỀ CHÚNG TÔI)
 * Based on Docx Item 9
 */
const AboutView = () => (
  <div className="p-6 pb-24 space-y-6">
     <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-teal-700">Về Dự Án</h2>
        <div className="w-16 h-1 bg-orange-400 mx-auto rounded-full"></div>
     </div>

     <Card className="space-y-4">
        <img 
          src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80" 
          alt="Team meeting" 
          className="w-full h-40 object-cover rounded-xl"
        />
        <div>
          <h3 className="font-bold text-slate-800 text-lg mb-2">Sứ mệnh của chúng tôi</h3>
          <p className="text-sm text-slate-600 leading-relaxed">
            Dự án "Rhythm of Signs" được thành lập với mục tiêu xóa bỏ rào cản ngôn ngữ. Chúng tôi mong muốn lan tỏa vẻ đẹp của Ngôn ngữ Ký hiệu (NNKH) tới cộng đồng, giúp mọi người hiểu và kết nối với nhau dễ dàng hơn.
          </p>
        </div>
     </Card>

     <div className="grid grid-cols-2 gap-4">
        <div className="bg-teal-50 p-4 rounded-xl">
           <h4 className="font-bold text-teal-700 mb-2 text-sm">Mục tiêu</h4>
           <p className="text-xs text-teal-600">Xây dựng cộng đồng học tập cởi mở, thân thiện và miễn phí.</p>
        </div>
        <div className="bg-orange-50 p-4 rounded-xl">
           <h4 className="font-bold text-orange-700 mb-2 text-sm">Định hướng</h4>
           <p className="text-xs text-orange-600">Phát triển AI nhận diện cử chỉ và mở rộng thư viện dữ liệu.</p>
        </div>
     </div>
  </div>
);

/**
 * VIEW: FORUM (DIỄN ĐÀN)
 * Based on Docx Item 8
 */
const ForumView = () => (
  <div className="p-4 pb-24 space-y-6">
     <SectionTitle title="DIỄN ĐÀN CỘNG ĐỒNG" subtitle="Thảo luận & Chia sẻ kiến thức" />
     
     <div className="flex gap-2 mb-4">
        <button className="flex-1 py-2 bg-teal-600 text-white rounded-lg text-sm font-bold shadow-md">Tất cả</button>
        <button className="flex-1 py-2 bg-white text-slate-600 border border-slate-200 rounded-lg text-sm font-medium">Bài báo</button>
        <button className="flex-1 py-2 bg-white text-slate-600 border border-slate-200 rounded-lg text-sm font-medium">Thảo luận</button>
     </div>

     {FORUM_POSTS.map(post => (
        <Card key={post.id} className="border-l-4 border-l-teal-500">
           <div className="flex justify-between items-start mb-2">
              <span className={`text-[10px] px-2 py-1 rounded-full uppercase font-bold ${post.type === 'article' ? 'bg-purple-100 text-purple-600' : 'bg-green-100 text-green-600'}`}>
                {post.type === 'article' ? 'Bài báo' : 'Thảo luận'}
              </span>
              <span className="text-xs text-slate-400">{post.date}</span>
           </div>
           <h3 className="font-bold text-slate-800 mb-2">{post.title}</h3>
           <p className="text-sm text-slate-600 mb-4 line-clamp-2">{post.content}</p>
           <div className="flex items-center gap-4 text-slate-400 text-xs pt-3 border-t border-slate-100">
              <div className="flex items-center gap-1"><User size={12}/> {post.user}</div>
              <div className="flex items-center gap-1 ml-auto"><Heart size={12}/> {post.likes}</div>
              <div className="flex items-center gap-1"><MessageSquare size={12}/> {post.comments}</div>
           </div>
        </Card>
     ))}
  </div>
);

/**
 * MAIN APP
 */
export default function App() {
  const [activeTab, setActiveTab] = useState('home');

  const renderContent = () => {
    switch(activeTab) {
      case 'home': return <HomeView onNavigate={setActiveTab} />;
      case 'library': return <LibraryView />;
      case 'forum': return <ForumView />;
      case 'practice': return <div className="p-10 text-center text-slate-400">Chức năng Luyện tập đang phát triển</div>;
      case 'about': return <AboutView />;
      default: return <HomeView onNavigate={setActiveTab} />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex justify-center font-sans selection:bg-teal-100">
      <div className="w-full max-w-md bg-white min-h-screen shadow-2xl relative flex flex-col">
        
        {/* Dynamic Header */}
        <header className="bg-white/90 backdrop-blur-sm text-slate-800 p-4 flex justify-between items-center sticky top-0 z-50 border-b border-slate-100">
          <div className="w-8 h-8 bg-teal-600 rounded-lg flex items-center justify-center shadow-teal-200 shadow-md">
            <span className="font-bold text-xs text-white">RoS</span>
          </div>
          <span className="font-bold text-sm tracking-widest uppercase text-slate-500">
            {activeTab === 'home' ? 'TRANG CHỦ' : 
             activeTab === 'library' ? 'TỪ ĐIỂN' : 
             activeTab === 'about' ? 'VỀ CHÚNG TÔI' : 'DIỄN ĐÀN'}
          </span>
          <div className="w-8"></div> {/* Spacer */}
        </header>

        <main className="flex-1 overflow-y-auto bg-slate-50">
          {renderContent()}
        </main>

        {/* Bottom Navigation */}
        <nav className="bg-white border-t border-slate-100 px-6 py-3 flex justify-between items-center sticky bottom-0 z-50 pb-6 safe-area-pb">
           {[
             { id: 'home', icon: Menu, label: 'Home' },
             { id: 'library', icon: BookOpen, label: 'Library' },
             { id: 'forum', icon: MessageSquare, label: 'Forum' },
             { id: 'about', icon: Info, label: 'About' }
           ].map(tab => (
             <button 
               key={tab.id}
               onClick={() => setActiveTab(tab.id)}
               className={`flex flex-col items-center gap-1 transition-colors ${activeTab === tab.id ? 'text-teal-600' : 'text-slate-300 hover:text-slate-400'}`}
             >
               <tab.icon size={24} strokeWidth={activeTab === tab.id ? 2.5 : 2} />
               <span className="text-[10px] font-bold">{tab.label}</span>
             </button>
           ))}
        </nav>

        {/* CSS for custom animations */}
        <style>{`
          @keyframes fade-in-up {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .animate-fade-in-up {
            animation: fade-in-up 0.8s ease-out forwards;
          }
          .no-scrollbar::-webkit-scrollbar {
            display: none;
          }
          .no-scrollbar {
            -ms-overflow-style: none;
            scrollbar-width: none;
          }
          .writing-vertical-lr {
            writing-mode: vertical-lr;
          }
        `}</style>

      </div>
    </div>
  );
}