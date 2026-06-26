import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import toast from 'react-hot-toast';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { Download, ChevronLeft, MessageSquare } from 'lucide-react';

export default function AnalysisDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAnalysis();
  }, [id]);

  const fetchAnalysis = async () => {
    try {
      // For now, assume this endpoint triggers analysis if not done, or fetches existing.
      // We will hit the analyze endpoint for a fresh resume if it's not analyzed yet.
      // The dashboard passes resume id, so let's hit analyze:
      const response = await api.post('/analysis/analyze', { resume_id: parseInt(id) });
      setAnalysis(response.data.analysis_results);
    } catch (error) {
      toast.error('Failed to load analysis report.');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    // Note: Since this creates a new analysis above, we'd normally fetch by the new analysis ID.
    toast.success(`Exporting as ${format.toUpperCase()}...`);
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-xl text-primary-600 animate-pulse">Running Deep AI Analysis...</div>
      </div>
    );
  }

  if (!analysis) return null;

  const radarData = [
    { subject: 'ATS Score', A: analysis.ats_score, fullMark: 100 },
    { subject: 'Job Match', A: analysis.match_percentage || 80, fullMark: 100 },
    { subject: 'Readability', A: analysis.resume_length_analysis?.word_count > 200 ? 90 : 60, fullMark: 100 },
    { subject: 'Impact Verbs', A: analysis.action_verb_analysis?.count > 5 ? 85 : 50, fullMark: 100 },
    { subject: 'Formatting', A: 90, fullMark: 100 },
  ];

  const pieData = [
    { name: 'Technical Skills', value: analysis.technical_skills?.length || 1 },
    { name: 'Soft Skills', value: analysis.soft_skills?.length || 1 },
    { name: 'Missing', value: analysis.missing_skills?.length || 1 }
  ];
  const COLORS = ['#0ea5e9', '#8b5cf6', '#ef4444'];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between md:items-center space-y-4 md:space-y-0">
        <button onClick={() => navigate(-1)} className="flex items-center text-slate-500 hover:text-primary-600">
          <ChevronLeft className="w-5 h-5 mr-1" /> Back to Dashboard
        </button>
        <div className="flex space-x-3">
          <button onClick={() => handleExport('pdf')} className="btn-secondary text-sm">
            <Download className="w-4 h-4 mr-2" /> PDF Report
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Stats & Charts */}
        <div className="lg:col-span-1 space-y-6">
          <div className="glass-card p-6 text-center">
            <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-200">ATS Score</h3>
            <div className={`text-6xl font-bold mt-4 ${analysis.ats_score > 75 ? 'text-green-500' : 'text-amber-500'}`}>
              {analysis.ats_score}
            </div>
          </div>

          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-200 mb-4 text-center">Resume Profile</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                  <PolarGrid stroke="#cbd5e1" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 12 }} />
                  <Radar name="Score" dataKey="A" stroke="#0ea5e9" fill="#0ea5e9" fillOpacity={0.5} />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-200 mb-4 text-center">Skills Distribution</h3>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    innerRadius={40}
                    outerRadius={70}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center space-x-4 mt-2">
              <div className="flex items-center text-xs text-slate-500"><div className="w-3 h-3 rounded-full bg-[#0ea5e9] mr-1"></div>Technical</div>
              <div className="flex items-center text-xs text-slate-500"><div className="w-3 h-3 rounded-full bg-[#8b5cf6] mr-1"></div>Soft</div>
              <div className="flex items-center text-xs text-slate-500"><div className="w-3 h-3 rounded-full bg-[#ef4444] mr-1"></div>Missing</div>
            </div>
          </div>
        </div>

        {/* Right Column: Detailed Breakdown */}
        <div className="lg:col-span-2 glass-card overflow-hidden flex flex-col">
          {/* Tabs */}
          <div className="flex border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
            <button 
              className={`px-6 py-4 text-sm font-medium transition-colors ${activeTab === 'overview' ? 'border-b-2 border-primary-500 text-primary-600' : 'text-slate-600 hover:text-slate-900 dark:text-slate-400'}`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button 
              className={`px-6 py-4 text-sm font-medium transition-colors ${activeTab === 'skills' ? 'border-b-2 border-primary-500 text-primary-600' : 'text-slate-600 hover:text-slate-900 dark:text-slate-400'}`}
              onClick={() => setActiveTab('skills')}
            >
              Skills & Keywords
            </button>
            <button 
              className={`px-6 py-4 text-sm font-medium transition-colors ${activeTab === 'suggestions' ? 'border-b-2 border-primary-500 text-primary-600' : 'text-slate-600 hover:text-slate-900 dark:text-slate-400'}`}
              onClick={() => setActiveTab('suggestions')}
            >
              Suggestions
            </button>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[70vh]">
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div>
                  <h4 className="text-xl font-semibold mb-2">Experience Summary</h4>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed">{analysis.experience_summary}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-100 dark:border-green-800">
                    <h5 className="font-semibold text-green-700 dark:text-green-400 mb-2">Strengths</h5>
                    <ul className="list-disc pl-5 space-y-1 text-sm text-green-800 dark:text-green-300">
                      {analysis.strengths?.map((item, i) => <li key={i}>{item}</li>)}
                    </ul>
                  </div>
                  <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-100 dark:border-red-800">
                    <h5 className="font-semibold text-red-700 dark:text-red-400 mb-2">Weaknesses</h5>
                    <ul className="list-disc pl-5 space-y-1 text-sm text-red-800 dark:text-red-300">
                      {analysis.weaknesses?.map((item, i) => <li key={i}>{item}</li>)}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'skills' && (
              <div className="space-y-6">
                <div>
                  <h4 className="text-xl font-semibold mb-3">Detected Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysis.skills_detected?.map((skill, i) => (
                      <span key={i} className="px-3 py-1 bg-primary-100 text-primary-700 dark:bg-primary-900/40 dark:text-primary-300 rounded-full text-sm font-medium">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="text-xl font-semibold mb-3">Missing Critical Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysis.missing_skills?.map((skill, i) => (
                      <span key={i} className="px-3 py-1 bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 rounded-full text-sm font-medium">
                        {skill}
                      </span>
                    ))}
                    {(!analysis.missing_skills || analysis.missing_skills.length === 0) && (
                      <span className="text-slate-500">Your resume perfectly matches all checked skills!</span>
                    )}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'suggestions' && (
              <div className="space-y-6">
                <div>
                  <h4 className="text-xl font-semibold mb-4 text-amber-600">Actionable Improvements</h4>
                  <div className="space-y-3">
                    {analysis.improvement_suggestions?.map((sugg, i) => (
                      <div key={i} className="flex items-start space-x-3 p-3 bg-amber-50 dark:bg-amber-900/10 rounded-lg border border-amber-100 dark:border-amber-800">
                        <div className="mt-0.5 w-2 h-2 bg-amber-500 rounded-full flex-shrink-0"></div>
                        <p className="text-sm text-amber-900 dark:text-amber-200">{sugg}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="text-xl font-semibold mb-4">Recruiter Tips</h4>
                  <ul className="space-y-2">
                    {analysis.recruiter_tips?.map((tip, i) => (
                      <li key={i} className="flex items-center text-slate-600 dark:text-slate-300 text-sm">
                        <MessageSquare className="w-4 h-4 mr-2 text-slate-400" />
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
