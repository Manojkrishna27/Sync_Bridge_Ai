import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ArrowRight, Check, X, HelpCircle, Layers, Zap } from 'lucide-react';

export default function OnboardingTour({ isOpen, onClose, onStartAutoMap }) {
  if (!isOpen) return null;

  const [step, setStep] = useState(0);

  const tourSteps = [
    {
      title: 'Welcome to AI Visual Mapping Studio',
      description: 'Easily bridge legacy enterprise schemas with modern cloud APIs using autonomous AI agent swarms and zero-code visual mapping.',
      icon: Zap
    },
    {
      title: 'Step 1: Upload Source & Target Schemas',
      description: 'Use the top navigation bar to upload XML, SOAP, JSON Schema, CSV, or Protobuf specifications.',
      icon: Layers
    },
    {
      title: 'Step 2: Generate AI Mappings',
      description: 'Click "Generate AI Mapping" to let our multi-agent AI copilot automatically analyze schemas and connect field pairs with confidence scores.',
      icon: Sparkles
    },
    {
      title: 'Step 3: Interactive Transformation Pipeline',
      description: 'Click any edge on the canvas to configure card-flip function transforms like Trim(), Uppercase(), and Replace().',
      icon: ArrowRight
    }
  ];

  const current = tourSteps[step];
  const Icon = current.icon;

  const handleNext = () => {
    if (step < tourSteps.length - 1) {
      setStep(step + 1);
    } else {
      onClose();
      onStartAutoMap();
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          className="w-full max-w-lg bg-slate-900 border border-indigo-500/40 rounded-3xl p-6 shadow-2xl text-white relative overflow-hidden"
        >
          <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold text-indigo-400 uppercase tracking-widest">
                Tour Step {step + 1} of {tourSteps.length}
              </span>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="flex items-start gap-4 mb-6">
            <div className="flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-cyan-400 text-white shadow-lg shrink-0">
              <Icon className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100 mb-1">{current.title}</h3>
              <p className="text-xs text-slate-300 leading-relaxed">{current.description}</p>
            </div>
          </div>

          {/* Dots Indicator */}
          <div className="flex items-center justify-between pt-4 border-t border-slate-800">
            <div className="flex items-center gap-1.5">
              {tourSteps.map((_, i) => (
                <div
                  key={i}
                  className={`w-2 h-2 rounded-full transition-all ${
                    i === step ? 'w-6 bg-cyan-400' : 'bg-slate-700'
                  }`}
                />
              ))}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={onClose}
                className="px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors"
              >
                Skip
              </button>
              <button
                onClick={handleNext}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white text-xs font-semibold shadow-lg shadow-indigo-500/30 transition-all hover:scale-105"
              >
                <span>{step === tourSteps.length - 1 ? 'Start Exploring' : 'Next'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
