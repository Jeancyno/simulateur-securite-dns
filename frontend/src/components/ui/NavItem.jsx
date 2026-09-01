import React from 'react';

const NavItem = ({
  icon: Icon,
  label,
  isActive = false,
  onClick,
  disabled = false,
  className = '',
  badge,
  ...props
}) => {
  const baseStyles = 'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none relative';

  const activeStyles = isActive
    ? 'bg-primary-50 text-primary-700 border-l-4 border-primary-600'
    : 'text-secondary-700 hover:bg-secondary-100 hover:text-secondary-900 border-l-4 border-transparent';

  const combinedClassName = `${baseStyles} ${activeStyles} ${className}`;

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={combinedClassName}
      aria-current={isActive ? 'page' : undefined}
      {...props}
    >
      {Icon && <Icon className="w-5 h-5 flex-shrink-0" />}
      <span className="font-medium truncate">{label}</span>
      {badge && (
        <span className="ml-auto bg-primary-600 text-white text-xs font-bold rounded-full px-2 py-0.5 flex-shrink-0">
          {badge}
        </span>
      )}
    </button>
  );
};

export default NavItem;
