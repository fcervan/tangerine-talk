import type { ReactNode } from "react";

type P = { className?: string; size?: number };
const make = (children: ReactNode) =>
  function Icon({ className = "", size = 22 }: P) {
    return (
      <svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth={1.75}
        strokeLinecap="round"
        strokeLinejoin="round"
        className={className}
        aria-hidden
      >
        {children}
      </svg>
    );
  };

export const ArrowIcon = make(<path d="M5 12h14M13 6l6 6-6 6" />);
export const MicIcon = make(<><path d="M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3z" /><path d="M19 11a7 7 0 0 1-14 0M12 18v3" /></>);
export const EarIcon = make(<><path d="M6 9a6 6 0 1 1 12 0c0 3-2 4-3 6s-1 4-3.5 4A3.5 3.5 0 0 1 8 15.5" /><path d="M9.5 9.5a2.5 2.5 0 0 1 5 0" /></>);
export const PenIcon = make(<><path d="M12 20h9" /><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z" /></>);
export const TestIcon = make(<><rect x="3" y="5" width="14" height="14" rx="3" /><path d="M7 3h12a2 2 0 0 1 2 2v12" /><path d="m7.5 12 2 2 3.5-4" /></>);
export const FlameIcon = make(<path d="M12 3c1 3.5 5 5.5 5 10a5 5 0 0 1-10 0c0-2 1-3 2-4 .3 1.2 1 2 2 2 0-3-1-5 1-8z" />);
export const TrophyIcon = make(<><path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z" /><path d="M17 5h3v2a3 3 0 0 1-3 3M7 5H4v2a3 3 0 0 0 3 3" /></>);
export const ChatIcon = make(<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1.1-4.2A8 8 0 1 1 21 12z" />);
export const TreeIcon = make(<><circle cx="12" cy="5" r="2.5" /><circle cx="5" cy="19" r="2.5" /><circle cx="19" cy="19" r="2.5" /><path d="M12 7.5V12M12 12 5 16.5M12 12l7 4.5" /></>);
export const LockIcon = make(<><rect x="5" y="11" width="14" height="9" rx="2.5" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /></>);
export const PlayIcon = make(<path d="M7 4.5v15l12-7.5z" />);
export const PauseIcon = make(<path d="M8 5v14M16 5v14" />);
export const CheckIcon = make(<path d="m5 12.5 4.5 4.5L19 7.5" />);
export const StarIcon = make(<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z" />);
export const BoltIcon = make(<path d="M13 2 4 14h7l-1 8 9-12h-7z" />);
export const MenuIcon = make(<path d="M4 7h16M4 12h16M4 17h16" />);
export const CloseIcon = make(<path d="M6 6l12 12M18 6 6 18" />);
