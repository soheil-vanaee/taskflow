import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
}

export default function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`bg-white shadow rounded-lg overflow-hidden ${className}`}>
      {children}
    </div>
  );
}

interface CardHeaderProps {
  children: ReactNode;
}

Card.Header = function CardHeader({ children }: CardHeaderProps) {
  return (
    <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
      {children}
    </div>
  );
};

interface CardBodyProps {
  children: ReactNode;
}

Card.Body = function CardBody({ children }: CardBodyProps) {
  return (
    <div className="px-4 py-5 sm:p-6">
      {children}
    </div>
  );
};

interface CardFooterProps {
  children: ReactNode;
}

Card.Footer = function CardFooter({ children }: CardFooterProps) {
  return (
    <div className="px-4 py-4 sm:px-6 bg-gray-50 border-t border-gray-200">
      {children}
    </div>
  );
};