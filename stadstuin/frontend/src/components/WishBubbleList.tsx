'use client';

import React from 'react';

interface Wish {
  name: string;
  wish: string;
}

interface WishBubbleListProps {
  wishes: Wish[];
}

const colors = [
  'bg-green-light text-green-dark',
  'bg-green-100 text-green-dark',
  'bg-green-200 text-green-dark',
];

export default function WishBubbleList({ wishes }: WishBubbleListProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
      {wishes.map((wish, index) => (
        <div
          key={wish.name + wish.wish}
          className={`rounded-lg p-4 relative ${colors[index % colors.length]} shadow-bubble`}
        >
          <div className="text-sm font-medium mb-2">
            {wish.name}
          </div>
          <div className="text-green-dark">
            {wish.wish}
          </div>
        </div>
      ))}
    </div>
  );
}
