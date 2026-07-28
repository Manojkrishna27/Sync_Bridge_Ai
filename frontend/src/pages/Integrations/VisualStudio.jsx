import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import confetti from 'canvas-confetti';

import HeaderBar from '../../components/studio/HeaderBar';
import SourcePanel from '../../components/studio/SourcePanel';
import TargetPanel from '../../components/studio/TargetPanel';
import MappingCanvas from '../../components/studio/MappingCanvas';
import AiCopilotProgress from '../../components/studio/AiCopilotProgress';
import AiAssistantWidget from '../../components/studio/AiAssistantWidget';
import TransformationModal from '../../components/studio/TransformationModal';
import PipelineFooter from '../../components/studio/PipelineFooter';
import SchemaUploadModal from '../../components/studio/SchemaUploadModal';
import ExportModal from '../../components/studio/ExportModal';
import OnboardingTour from '../../components/studio/OnboardingTour';

export default function VisualStudio() {
  const [mappingName, setMappingName] = useState('SOAP Customer Sync ➔ REST Customer API');
  const [searchTerm, setSearchTerm] = useState('');

  // Source & Target field definitions as requested
  const [sourceFields, setSourceFields] = useState([
    { name: 'CustomerID', type: 'string', isConnected: false },
    { name: 'Name', type: 'string', isConnected: false },
    { name: 'Email', type: 'string', isConnected: false },
    { name: 'Phone', type: 'string', isConnected: false },
    { name: 'Address', type: 'string', isConnected: false },
    { name: 'Country', type: 'string', isConnected: false },
    { name: 'CreatedDate', type: 'date', isConnected: false }
  ]);

  const [targetFields, setTargetFields] = useState([
    { name: 'customer_id', type: 'string', isConnected: false },
    { name: 'full_name', type: 'string', isConnected: false },
    { name: 'email_address', type: 'string', isConnected: false },
    { name: 'mobile', type: 'string', isConnected: false },
    { name: 'location', type: 'string', isConnected: false },
    { name: 'country', type: 'string', isConnected: false },
    { name: 'created_at', type: 'timestamp', isConnected: false }
  ]);

  // Active connections
  const [connections, setConnections] = useState([]);
  const [history, setHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  // Interaction states
  const [hoveredField, setHoveredField] = useState(null);
  const [selectedField, setSelectedField] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [activeTransformationEdge, setActiveTransformationEdge] = useState(null);

  // AI & Pipeline states
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [aiStage, setAiStage] = useState(0);
  const [aiProgress, setAiProgress] = useState(0);
  const [isExecutingPipeline, setIsExecutingPipeline] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [validationStatus, setValidationStatus] = useState(null);

  // Modals & Tour
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [uploadType, setUploadType] = useState('source');
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [isTourOpen, setIsTourOpen] = useState(false);

  // Auto connect mappings list
  const prebuiltMappings = [
    { id: 'c1', source: 'CustomerID', target: 'customer_id', confidence: 98 },
    { id: 'c2', source: 'Name', target: 'full_name', confidence: 95 },
    { id: 'c3', source: 'Email', target: 'email_address', confidence: 98 },
    { id: 'c4', source: 'Phone', target: 'mobile', confidence: 87 },
    { id: 'c5', source: 'Address', target: 'location', confidence: 82 },
    { id: 'c6', source: 'Country', target: 'country', confidence: 99 },
    { id: 'c7', source: 'CreatedDate', target: 'created_at', confidence: 94 }
  ];

  // AI Generate Mappings sequence
  const handleGenerateAiMapping = () => {
    setIsAnalyzing(true);
    setAiStage(0);
    setAiProgress(10);
    setConnections([]);

    // Reset field connection indicators
    setSourceFields((prev) => prev.map((f) => ({ ...f, isConnected: false })));
    setTargetFields((prev) => prev.map((f) => ({ ...f, isConnected: false })));

    // Stage 1: Analyze
    const t1 = setTimeout(() => {
      setAiStage(1);
      setAiProgress(45);
    }, 800);

    // Stage 2: Relationships
    const t2 = setTimeout(() => {
      setAiStage(2);
      setAiProgress(75);
    }, 1600);

    // Stage 3: Synthesize and auto connect sequentially
    const t3 = setTimeout(() => {
      setAiStage(3);
      setAiProgress(100);

      // Connect each field pair one by one
      prebuiltMappings.forEach((mapping, idx) => {
        setTimeout(() => {
          setConnections((prev) => {
            if (prev.some((c) => c.id === mapping.id)) return prev;
            return [...prev, mapping];
          });

          setSourceFields((prev) =>
            prev.map((f) => (f.name === mapping.source ? { ...f, isConnected: true } : f))
          );
          setTargetFields((prev) =>
            prev.map((f) => (f.name === mapping.target ? { ...f, isConnected: true } : f))
          );

          // Confetti on last item
          if (idx === prebuiltMappings.length - 1) {
            confetti({
              particleCount: 80,
              spread: 70,
              origin: { y: 0.6 }
            });
          }
        }, idx * 250);
      });
    }, 2400);

    const t4 = setTimeout(() => {
      setIsAnalyzing(false);
    }, 4500);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
    };
  };

  // Handle Validation
  const handleValidate = () => {
    setIsValidating(true);
    setIsExecutingPipeline(true);

    setTimeout(() => {
      setIsValidating(false);
      setValidationStatus('success');
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.7 }
      });
    }, 2200);
  };

  // Undo & Redo Handlers
  const handleUndo = () => {
    if (connections.length > 0) {
      setConnections((prev) => prev.slice(0, -1));
    }
  };

  const handleRedo = () => {
    if (connections.length < prebuiltMappings.length) {
      const nextMapping = prebuiltMappings[connections.length];
      setConnections((prev) => [...prev, nextMapping]);
    }
  };

  const handleSaveTransformation = (edgeId, updatedTransforms) => {
    setConnections((prev) =>
      prev.map((c) => (c.id === edgeId ? { ...c, transforms: updatedTransforms } : c))
    );
  };

  const handleOpenUploadModal = (type) => {
    setUploadType(type);
    setIsUploadModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans overflow-hidden">
      {/* Top Header Bar */}
      <HeaderBar
        mappingName={mappingName}
        setMappingName={setMappingName}
        onOpenSourceModal={() => handleOpenUploadModal('source')}
        onOpenTargetModal={() => handleOpenUploadModal('target')}
        onGenerateAiMapping={handleGenerateAiMapping}
        onValidate={handleValidate}
        onPreview={() => setIsExportModalOpen(true)}
        onExport={() => setIsExportModalOpen(true)}
        onUndo={handleUndo}
        onRedo={handleRedo}
        onStartTour={() => setIsTourOpen(true)}
        isAnalyzing={isAnalyzing}
        isValidating={isValidating}
        validationStatus={validationStatus}
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
      />

      {/* AI Copilot Stage Progress Overlay */}
      <AiCopilotProgress
        isAnalyzing={isAnalyzing}
        currentStage={aiStage}
        stageProgress={aiProgress}
      />

      {/* Main 3-Column Mapping Studio Layout */}
      <div className="flex-1 flex items-stretch gap-4 p-4 max-w-[1920px] w-full mx-auto overflow-hidden">
        {/* Left Panel: Source Schema */}
        <SourcePanel
          fields={sourceFields}
          hoveredField={hoveredField}
          setHoveredField={setHoveredField}
          selectedField={selectedField}
          setSelectedField={setSelectedField}
          searchTerm={searchTerm}
        />

        {/* Center Panel: Animated Mapping Canvas */}
        <MappingCanvas
          connections={connections}
          hoveredField={hoveredField}
          setHoveredField={setHoveredField}
          selectedEdge={selectedEdge}
          setSelectedEdge={setSelectedEdge}
          onOpenTransformation={(edge) => setActiveTransformationEdge(edge)}
        />

        {/* Right Panel: Target Schema */}
        <TargetPanel
          fields={targetFields}
          hoveredField={hoveredField}
          setHoveredField={setHoveredField}
          selectedField={selectedField}
          setSelectedField={setSelectedField}
          searchTerm={searchTerm}
        />
      </div>

      {/* Bottom Panel: Live Execution Pipeline */}
      <PipelineFooter
        isExecuting={isExecutingPipeline}
        onRunPipeline={() => {
          setIsExecutingPipeline(true);
          setTimeout(() => setIsExecutingPipeline(false), 2600);
        }}
      />

      {/* Floating AI Copilot Widget (Bottom Right) */}
      <AiAssistantWidget
        status={isAnalyzing ? 'thinking' : 'idle'}
        totalConnections={connections.length}
        onAutoMap={handleGenerateAiMapping}
      />

      {/* Modals */}
      <TransformationModal
        edge={activeTransformationEdge}
        onClose={() => setActiveTransformationEdge(null)}
        onSaveTransformation={handleSaveTransformation}
      />

      <SchemaUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        type={uploadType}
        onSaveSchema={() => {}}
      />

      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        connections={connections}
        mappingName={mappingName}
      />

      <OnboardingTour
        isOpen={isTourOpen}
        onClose={() => setIsTourOpen(false)}
        onStartAutoMap={handleGenerateAiMapping}
      />
    </div>
  );
}
