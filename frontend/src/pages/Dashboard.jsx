import React, { useState, useEffect, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileText, Trash2, BarChart2 } from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const [resumes, setResumes] = useState([]);
  const [isUploading, setIsUploading] = useState(false);

  const fetchResumes = async () => {
    try {
      const response = await api.get('/resumes');
      setResumes(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, []);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    const toastId = toast.loading('Uploading resume...');
    
    try {
      await api.post('/resumes/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      toast.success('Resume uploaded successfully!', { id: toastId });
      fetchResumes();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Upload failed', { id: toastId });
    } finally {
      setIsUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxSize: 10 * 1024 * 1024,
    multiple: false
  });

  const deleteResume = async (id) => {
    if (!window.confirm('Are you sure you want to delete this resume?')) return;
    try {
      await api.delete(`/resumes/${id}`);
      toast.success('Resume deleted');
      fetchResumes();
    } catch (err) {
      toast.error('Failed to delete resume');
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Your Resumes</h1>
      </div>

      <div 
        {...getRootProps()} 
        className={`glass-card p-12 border-2 border-dashed flex flex-col items-center justify-center cursor-pointer transition-colors ${
          isDragActive ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-slate-300 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800'
        } ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}
      >
        <input {...getInputProps()} />
        <UploadCloud className={`w-16 h-16 mb-4 ${isDragActive ? 'text-primary-500' : 'text-slate-400'}`} />
        <h3 className="text-xl font-medium text-slate-700 dark:text-slate-200">
          {isDragActive ? 'Drop your resume here' : 'Drag & drop a PDF resume here'}
        </h3>
        <p className="mt-2 text-sm text-slate-500">or click to select a file (Max 10MB)</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {resumes.map((resume) => (
          <div key={resume.id} className="glass-card p-6 flex flex-col hover:-translate-y-1 transition-transform duration-200">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3 overflow-hidden">
                <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                  <FileText className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                </div>
                <div className="overflow-hidden">
                  <h4 className="font-semibold text-slate-900 dark:text-white truncate pr-2">{resume.filename}</h4>
                  <p className="text-xs text-slate-500">{new Date(resume.uploaded_at).toLocaleDateString()}</p>
                </div>
              </div>
              <button onClick={() => deleteResume(resume.id)} className="text-slate-400 hover:text-red-500 transition-colors flex-shrink-0">
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
            
            <div className="mt-auto pt-4 flex space-x-2">
              <Link to={`/analysis/${resume.id}`} className="btn-primary w-full flex items-center justify-center space-x-2">
                <BarChart2 className="w-4 h-4" />
                <span>Analyze</span>
              </Link>
            </div>
          </div>
        ))}
        {resumes.length === 0 && (
          <div className="col-span-full py-12 text-center text-slate-500">
            No resumes uploaded yet. Upload one above to get started!
          </div>
        )}
      </div>
    </div>
  );
}
