import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  isDisabled = false,
  icon: Icon = null,
  onClick,
  type = 'button',
  className = '',
  ariaLabel,
  ...props
}) {
  const variantStyles = {
    primary: 'bg-blue-600 hover:bg-blue-500 text-white shadow-sm hover:shadow-lg shadow-blue-500/20 border border-blue-500/30',
    secondary: 'bg-slate-800 hover:bg-slate-700 text-slate-100 shadow-sm border border-slate-700',
    outline: 'bg-transparent hover:bg-slate-800/60 text-slate-300 hover:text-white border border-slate-700 hover:border-slate-600',
    ghost: 'bg-transparent hover:bg-slate-800/50 text-slate-400 hover:text-white border border-transparent',
    danger: 'bg-red-600 hover:bg-red-500 text-white shadow-sm hover:shadow-lg shadow-red-500/20 border border-red-500/30',
    success: 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm hover:shadow-lg shadow-emerald-500/20 border border-emerald-500/30'
  };

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-xs rounded-xl gap-1.5',
    md: 'px-4 py-2 text-sm rounded-xl gap-2',
    lg: 'px-5 py-2.5 text-base rounded-2xl gap-2.5'
  };

  return (
    <motion.button
      whileHover={{ scale: isDisabled || isLoading ? 1 : 1.02 }}
      whileTap={{ scale: isDisabled || isLoading ? 1 : 0.98 }}
      type={type}
      onClick={onClick}
      disabled={isDisabled || isLoading}
      aria-label={ariaLabel}
      className={`inline-flex items-center justify-center font-medium font-sans transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:opacity-50 disabled:cursor-not-allowed select-none ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin text-current shrink-0" />
      ) : Icon ? (
        <Icon className="w-4 h-4 shrink-0" />
      ) : null}
      <span>{children}</span>
    </motion.button>
  );
}
