import React, { useState, useEffect, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Lock, Mail, Eye, EyeOff, User, ArrowRight, Zap, Shield, Globe } from 'lucide-react';
import api from '../../services/api';

// ─── Animated background canvas ────────────────────────────────────────────
function ParticleCanvas() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let animId;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    const NUM = 60;
    const particles = Array.from({ length: NUM }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 2 + 0.5,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      alpha: Math.random() * 0.5 + 0.1,
    }));

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach((p, i) => {
        particles.slice(i + 1).forEach((q) => {
          const dx = p.x - q.x;
          const dy = p.y - q.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 120) {
            ctx.beginPath();
            ctx.strokeStyle = `rgba(139,92,246,${0.12 * (1 - dist / 120)})`;
            ctx.lineWidth = 0.6;
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(q.x, q.y);
            ctx.stroke();
          }
        });

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(167,139,250,${p.alpha})`;
        ctx.fill();

        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
      });

      animId = requestAnimationFrame(draw);
    };

    draw();
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return <canvas ref={canvasRef} className="pointer-events-none fixed inset-0 z-0" />;
}

function FeaturePill({ icon: Icon, label }) {
  return (
    <div className="flex items-center gap-2 rounded-full border border-violet-500/20 bg-violet-500/10 px-3 py-1.5 backdrop-blur-sm">
      <Icon className="h-3.5 w-3.5 text-violet-400" />
      <span className="text-xs font-medium text-violet-300">{label}</span>
    </div>
  );
}

function AuthInput({ id, type: initialType = 'text', placeholder, icon: Icon, register, error, label }) {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = initialType === 'password';
  const type = isPassword ? (showPassword ? 'text' : 'password') : initialType;

  return (
    <div className="group">
      <label htmlFor={id} className="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-slate-400">
        {label}
      </label>
      <div className="relative">
        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
          <Icon className="h-4 w-4 text-slate-500 transition-colors group-focus-within:text-violet-400" />
        </div>
        <input
          id={id}
          type={type}
          placeholder={placeholder}
          {...register}
          className={`w-full rounded-xl border bg-slate-800/60 py-3 pl-11 text-sm text-slate-100 placeholder-slate-500 backdrop-blur-sm transition-all duration-200
            focus:border-violet-500 focus:outline-none focus:ring-2 focus:ring-violet-500/20
            ${error ? 'border-red-500/60 focus:border-red-500 focus:ring-red-500/20' : 'border-slate-700/60 hover:border-slate-600'}
            ${isPassword ? 'pr-11' : 'pr-4'}`}
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setShowPassword((v) => !v)}
            className="absolute inset-y-0 right-0 flex items-center pr-4 text-slate-500 transition-colors hover:text-violet-400"
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        )}
      </div>
      {error && (
        <p className="mt-1.5 flex items-center gap-1 text-xs text-red-400">
          <span className="inline-block h-1 w-1 rounded-full bg-red-400" />
          {error.message}
        </p>
      )}
    </div>
  );
}

function SubmitButton({ loading, label }) {
  return (
    <button
      type="submit"
      disabled={loading}
      className="group relative flex w-full items-center justify-center gap-2 overflow-hidden rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 py-3 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 transition-all duration-300 hover:from-violet-500 hover:to-indigo-500 hover:shadow-violet-500/40 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:cursor-not-allowed disabled:opacity-60"
    >
      <span className="absolute inset-0 -translate-x-full bg-white/10 skew-x-12 transition-transform duration-500 group-hover:translate-x-full" />
      {loading ? (
        <>
          <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          <span>Processing…</span>
        </>
      ) : (
        <>
          <span>{label}</span>
          <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
        </>
      )}
    </button>
  );
}

export default function AuthPage() {
  const [mode, setMode] = useState('login');
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const loginForm = useForm();
  const signupForm = useForm();

  useEffect(() => {
    setErrorMsg('');
    setSuccessMsg('');
  }, [mode]);

  const onLogin = async (data) => {
    setIsSubmitting(true);
    setErrorMsg('');
    try {
      await login(data.email, data.password);
      navigate('/');
    } catch (err) {
      setErrorMsg(err.response?.data?.message || 'Invalid email or password.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const onSignup = async (data) => {
    if (data.password !== data.confirmPassword) {
      signupForm.setError('confirmPassword', { message: 'Passwords do not match' });
      return;
    }
    setIsSubmitting(true);
    setErrorMsg('');
    try {
      await api.post('/auth/register', {
        name: data.name,
        email: data.email,
        password: data.password,
      });
      setSuccessMsg('Account created! You can now sign in.');
      setMode('login');
      loginForm.setValue('email', data.email);
    } catch (err) {
      setErrorMsg(err.response?.data?.message || 'Registration failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#080b14] px-4 py-12">
      <ParticleCanvas />

      {/* Gradient orbs */}
      <div className="pointer-events-none fixed inset-0 z-0">
        <div className="absolute -left-40 -top-40 h-96 w-96 rounded-full bg-violet-600/20 blur-[120px]" />
        <div className="absolute -bottom-40 -right-40 h-96 w-96 rounded-full bg-indigo-600/20 blur-[120px]" />
        <div className="absolute left-1/2 top-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full bg-purple-500/10 blur-[80px]" />
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Logo */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-600 shadow-lg shadow-violet-500/30 ring-1 ring-white/10">
            <Zap className="h-7 w-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Sync<span className="bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">Bridge</span>
            <span className="ml-1 text-slate-400">AI</span>
          </h1>
          <p className="mt-1 text-sm text-slate-500">Intelligent Integration Platform</p>
        </div>

        {/* Feature pills */}
        <div className="mb-6 flex flex-wrap justify-center gap-2">
          <FeaturePill icon={Shield} label="Enterprise Secure" />
          <FeaturePill icon={Globe} label="Multi-Protocol" />
          <FeaturePill icon={Zap} label="AI-Powered" />
        </div>

        {/* Card */}
        <div className="rounded-2xl border border-slate-700/50 bg-slate-900/70 p-8 shadow-2xl shadow-black/50 backdrop-blur-xl ring-1 ring-white/5">
          {/* Tab switcher */}
          <div className="mb-8 flex rounded-xl bg-slate-800/60 p-1">
            {['login', 'signup'].map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setMode(tab)}
                className={`flex-1 rounded-lg py-2.5 text-sm font-semibold transition-all duration-300 ${
                  mode === tab
                    ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-lg shadow-violet-500/20'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tab === 'login' ? 'Sign In' : 'Sign Up'}
              </button>
            ))}
          </div>

          {/* LOGIN */}
          {mode === 'login' && (
            <div>
              <div className="mb-6">
                <h2 className="text-xl font-bold text-white">Welcome back</h2>
                <p className="mt-1 text-sm text-slate-400">Sign in to your workspace</p>
              </div>
              <form onSubmit={loginForm.handleSubmit(onLogin)} className="space-y-5">
                <AuthInput
                  id="login-email"
                  type="email"
                  label="Email"
                  placeholder="you@company.com"
                  icon={Mail}
                  register={loginForm.register('email', { required: 'Email is required' })}
                  error={loginForm.formState.errors.email}
                />
                <AuthInput
                  id="login-password"
                  type="password"
                  label="Password"
                  placeholder="••••••••"
                  icon={Lock}
                  register={loginForm.register('password', { required: 'Password is required' })}
                  error={loginForm.formState.errors.password}
                />
                <div className="flex items-center justify-between">
                  <label className="flex cursor-pointer items-center gap-2">
                    <input type="checkbox" className="h-3.5 w-3.5 accent-violet-500" />
                    <span className="text-xs text-slate-400">Remember me</span>
                  </label>
                  <a href="/forgot-password" className="text-xs font-medium text-violet-400 transition-colors hover:text-violet-300">
                    Forgot password?
                  </a>
                </div>
                {errorMsg && (
                  <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">{errorMsg}</div>
                )}
                {successMsg && (
                  <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-400">{successMsg}</div>
                )}
                <SubmitButton loading={isSubmitting} label="Sign In" />
              </form>
              <p className="mt-6 text-center text-xs text-slate-500">
                Don&apos;t have an account?{' '}
                <button type="button" onClick={() => setMode('signup')} className="font-medium text-violet-400 transition-colors hover:text-violet-300">
                  Create one free
                </button>
              </p>
            </div>
          )}

          {/* SIGNUP */}
          {mode === 'signup' && (
            <div>
              <div className="mb-6">
                <h2 className="text-xl font-bold text-white">Create your account</h2>
                <p className="mt-1 text-sm text-slate-400">Start integrating in minutes</p>
              </div>
              <form onSubmit={signupForm.handleSubmit(onSignup)} className="space-y-5">
                <AuthInput
                  id="signup-name"
                  type="text"
                  label="Full Name"
                  placeholder="Alex Johnson"
                  icon={User}
                  register={signupForm.register('name', { required: 'Name is required' })}
                  error={signupForm.formState.errors.name}
                />
                <AuthInput
                  id="signup-email"
                  type="email"
                  label="Work Email"
                  placeholder="you@company.com"
                  icon={Mail}
                  register={signupForm.register('email', {
                    required: 'Email is required',
                    pattern: { value: /^\S+@\S+\.\S+$/, message: 'Invalid email format' },
                  })}
                  error={signupForm.formState.errors.email}
                />
                <AuthInput
                  id="signup-password"
                  type="password"
                  label="Password"
                  placeholder="Min. 8 characters"
                  icon={Lock}
                  register={signupForm.register('password', {
                    required: 'Password is required',
                    minLength: { value: 8, message: 'At least 8 characters required' },
                  })}
                  error={signupForm.formState.errors.password}
                />
                <AuthInput
                  id="signup-confirm-password"
                  type="password"
                  label="Confirm Password"
                  placeholder="Repeat your password"
                  icon={Lock}
                  register={signupForm.register('confirmPassword', { required: 'Please confirm your password' })}
                  error={signupForm.formState.errors.confirmPassword}
                />
                {errorMsg && (
                  <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">{errorMsg}</div>
                )}
                <p className="text-xs text-slate-500">
                  By signing up you agree to our{' '}
                  <a href="#" className="text-violet-400 hover:text-violet-300">Terms</a>
                  {' '}&amp;{' '}
                  <a href="#" className="text-violet-400 hover:text-violet-300">Privacy Policy</a>.
                </p>
                <SubmitButton loading={isSubmitting} label="Create Account" />
              </form>
              <p className="mt-6 text-center text-xs text-slate-500">
                Already have an account?{' '}
                <button type="button" onClick={() => setMode('login')} className="font-medium text-violet-400 transition-colors hover:text-violet-300">
                  Sign in
                </button>
              </p>
            </div>
          )}
        </div>

        <p className="mt-6 text-center text-xs text-slate-600">
          © {new Date().getFullYear()} SyncBridge AI · All rights reserved
        </p>
      </div>
    </div>
  );
}
