'use client';

import React, { useState } from 'react';
import { toast } from 'react-hot-toast';

interface WishInputProps {
  onAddWish: (wish: { name: string; wish: string }) => void;
}

export default function WishInput({ onAddWish }: WishInputProps) {
  const [name, setName] = useState('');
  const [wish, setWish] = useState('');
  const [nameError, setNameError] = useState(false);
  const [wishError, setWishError] = useState(false);

  const handleAddWish = () => {
    let hasErrors = false;
    if (!name.trim()) {
      setNameError(true);
      hasErrors = true;
    } else {
      setNameError(false);
    }
    if (!wish.trim()) {
      setWishError(true);
      hasErrors = true;
    } else {
      setWishError(false);
    }
    if (hasErrors) {
      toast.error('Vul zowel naam als wens in');
      return;
    }
    try {
      onAddWish({ name, wish });
      setName('');
      setWish('');
      toast.success('Wens toegevoegd!');
    } catch (err) {
      toast.error('Er is een fout opgetreden bij het toevoegen van de wens');
      console.error('Error adding wish:', err);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAddWish();
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-green-dark">
          Naam
        </label>
        <input
          type="text"
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className={`mt-1 block w-full rounded-md ${
            nameError ? 'border-red-500' : 'border-green-light'
          } shadow-bubble focus:border-green-primary focus:ring-green-primary sm:text-sm`}
          placeholder="Je naam"
        />
        {nameError && (
          <p className="mt-1 text-sm text-red-500">Vul je naam in</p>
        )}
      </div>

      <div>
        <label htmlFor="wish" className="block text-sm font-medium text-green-dark">
          Wens
        </label>
        <div className="flex gap-2 items-end">
          <textarea
            id="wish"
            value={wish}
            onChange={(e) => setWish(e.target.value)}
            onKeyDown={handleKeyDown}
            className={`mt-1 block w-full rounded-md ${
              wishError ? 'border-red-500' : 'border-green-light'
            } shadow-bubble focus:border-green-primary focus:ring-green-primary sm:text-sm`}
            placeholder="Je wens voor de stadstuin"
            rows={4}
          />
          <button
            type="button"
            onClick={handleAddWish}
            className="mb-1 flex items-center justify-center bg-green-primary text-white rounded-full w-10 h-10 text-2xl hover:bg-green-dark focus:outline-none focus:ring-2 focus:ring-green-primary focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={!name.trim() || !wish.trim()}
            aria-label="Voeg wens toe"
          >
            +
          </button>
        </div>
        {wishError && (
          <p className="mt-1 text-sm text-red-500">Vul je wens in</p>
        )}
      </div>
    </div>
  );
}
