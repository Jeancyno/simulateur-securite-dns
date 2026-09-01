import React from 'react';
import { Shield } from 'lucide-react';

const Logo = ({
  title = 'DNS Security',
  subtitle = 'Simulateur',
  size = 'md',
  showIcon = true,
  className = '',
}) => {
  const sizes = {
    sm: {
      icon: 'w-6 h-6 sm:w-8 sm:h-8',
      title: 'text-lg sm:text-xl',
      subtitle: 'text-xs sm:text-sm',
      container: 'gap-1.5 sm:gap-2',
    },
    md: {
      icon: 'w-8 h-8 sm:w-10 sm:h-10',
      title: 'text-xl sm:text-2xl',
      subtitle: 'text-sm sm:text-base',
      container: 'gap-2 sm:gap-3',
    },
    lg: {
      icon: 'w-10 h-10 sm:w-12 sm:h-12',
      title: 'text-2xl sm:text-3xl',
      subtitle: 'text-base sm:text-lg',
      container: 'gap-2.5 sm:gap-3',
    },
  };

  const currentSize = sizes[size] || sizes.md;

  return (
    <div className={`flex items-center ${currentSize.container} ${className}`}>
      {showIcon && (
        <Shield className={`${currentSize.icon} text-primary-600 flex-shrink-0`} />
      )}
      <div className="flex flex-col">
        <span className={`${currentSize.title} font-bold text-secondary-900 leading-tight`}>
          {title}
        </span>
        {subtitle && (
          <span className={`${currentSize.subtitle} text-secondary-600 font-medium leading-tight`}>
            {subtitle}
          </span>
        )}
      </div>
    </div>
  );
};

export default Logo;
