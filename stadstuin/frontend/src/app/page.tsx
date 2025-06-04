'use client';

import Image from "next/image";
import { useState } from 'react';
import WishInput from '@/components/WishInput';
import WishBubbleList from '@/components/WishBubbleList';
import api from '@/utils/api';
import { toast } from 'react-hot-toast';

export default function Home() {
  const [wishes, setWishes] = useState<{ name: string; wish: string }[]>([]);
  const [prompt, setPrompt] = useState<string>('');
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  const handleAddWish = (wish: { name: string; wish: string }) => {
    setWishes((prev) => [...prev, wish]);
  };

  const handleCombineWishes = async () => {
    if (wishes.length === 0) {
      toast.error('Voeg eerst wensen toe voordat je wensen combineert');
      return;
    }

    setErrorMessage(null);
    setLoading(true);

    try {
      // Get prompt from wishes
      const promptResponse = await api.post('/build_prompt', { wishes });
      const generatedPrompt = (promptResponse.data as { prompt: string }).prompt;
      setPrompt(generatedPrompt);
      toast.success('Wensen succesvol gecombineerd!');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error 
        ? err.message 
        : typeof err === 'object' && err !== null && 'response' in err
          ? (err as { response: { data: { error?: string } } }).response?.data?.error 
          : 'Er is een fout opgetreden bij het combineren van de wensen';
      
      toast.error(errorMessage || 'Er is een fout opgetreden bij het combineren van de wensen');
      setErrorMessage(errorMessage || 'Er is een fout opgetreden bij het combineren van de wensen');
    } finally {
      setLoading(false);
    }
  };

  const toggleEditing = () => {
    setIsEditing(!isEditing);
  };

  const handleBuildGarden = async () => {
    if (!prompt) {
      toast.error('Combineer eerst je wensen om een prompt te genereren');
      return;
    }

    setErrorMessage(null);
    setLoading(true);

    try {
      // Generate image from prompt
      const imageResponse = await api.post('/generate_image', { prompt });
      const imageUrl = (imageResponse.data as { imageUrl: string }).imageUrl;

      setImageUrl(imageUrl);
      toast.success('Stadstuin succesvol gegenereerd!');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error 
        ? err.message 
        : typeof err === 'object' && err !== null && 'response' in err
          ? (err as { response: { data: { error?: string } } }).response?.data?.error 
          : 'Er is een fout opgetreden bij het genereren van de stadstuin';
      
      toast.error(errorMessage || 'Er is een fout opgetreden bij het genereren van de stadstuin');
      setErrorMessage(errorMessage || 'Er is een fout opgetreden bij het genereren van de stadstuin');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-green-light">
      <main className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-green-dark mb-4">
              Bouw je eigen stadstuin
            </h1>
            <p className="text-xl text-green-dark/80">
              Deel je wensen voor een groenere stad en laat ons je stadstuin ontwerpen!
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left: Input */}
            <div className="flex flex-col gap-6">
              <WishInput onAddWish={handleAddWish} />
              <button
                onClick={handleCombineWishes}
                disabled={loading || wishes.length === 0}
                className="w-full bg-green-primary text-white py-3 px-4 rounded-md hover:bg-green-dark focus:outline-none focus:ring-2 focus:ring-green-primary focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed mb-6"
              >
                {loading ? 'Bezig met combineren...' : 'Combineer wensen'}
              </button>
              
              {prompt && (
                <div className="mt-6 p-4 bg-white rounded shadow">
                  {isEditing 
                    ? <textarea 
                        className="w-full p-2 border rounded" 
                        value={prompt} 
                        onChange={e => setPrompt(e.target.value)} 
                        rows={6} 
                      />  
                    : <pre className="whitespace-pre-wrap">{prompt}</pre>
                  }
                  <div className="mt-4 flex space-x-4">
                    <button
                      onClick={toggleEditing}
                      className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
                    >
                      {isEditing ? 'Opslaan' : 'Prompt aanpassen'}
                    </button>
                    <button
                      onClick={handleBuildGarden}
                      disabled={loading}
                      className="px-4 py-2 bg-green-primary text-white rounded hover:bg-green-dark focus:outline-none focus:ring-2 focus:ring-green-primary focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loading ? 'Bezig met genereren...' : 'Bouw mijn stadstuin'}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Right: Chat bubbles */}
            <div className="flex flex-col items-end gap-2">
              <WishBubbleList wishes={wishes} />
              {errorMessage && (
                <div className="bg-red-50 text-red-700 p-4 rounded-md mb-6 w-full">
                  {errorMessage}
                </div>
              )}
              {imageUrl && (
                <div className="relative aspect-square w-full max-w-md mt-4">
                  <Image
                    src={imageUrl}
                    alt="Generated stadstuin"
                    fill
                    className="object-cover rounded-lg"
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
