import { memo } from "react";

const LoadingSkeleton = memo(() => (
  <div className="animate-pulse">
    <div className="flex items-center gap-3 p-4 rounded-xl bg-gray-50">
      {/* Avatar skeleton */}
      <div className="w-12 h-12 bg-gray-300 rounded-full"></div>
      
      <div className="flex-1">
        {/* Name skeleton */}
        <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
        {/* Username skeleton */}
        <div className="h-3 bg-gray-200 rounded w-1/2 mb-1"></div>
        {/* Followers skeleton */}
        <div className="h-3 bg-gray-200 rounded w-1/3"></div>
      </div>
      
      <div className="flex gap-2">
        {/* Follow button skeleton */}
        <div className="h-8 w-16 bg-gray-300 rounded-full"></div>
        {/* Chat button skeleton */}
        <div className="h-8 w-12 bg-gray-200 rounded-full"></div>
      </div>
    </div>
  </div>
));

const PostSkeleton = memo(() => (
  <div className="animate-pulse bg-white rounded-xl overflow-hidden shadow-sm border border-gray-100">
    {/* Post header skeleton */}
    <div className="flex items-center gap-3 p-4 border-b border-gray-100">
      <div className="w-10 h-10 bg-gray-300 rounded-full"></div>
      <div className="flex-1">
        <div className="h-4 bg-gray-300 rounded w-1/3 mb-1"></div>
        <div className="h-3 bg-gray-200 rounded w-1/4"></div>
      </div>
    </div>
    
    {/* Post image skeleton */}
    <div className="aspect-square bg-gray-300"></div>
    
    {/* Post actions skeleton */}
    <div className="p-4">
      <div className="flex items-center gap-4 mb-2">
        <div className="h-6 w-12 bg-gray-200 rounded"></div>
        <div className="h-6 w-12 bg-gray-200 rounded"></div>
        <div className="h-6 w-6 bg-gray-200 rounded"></div>
      </div>
      <div className="h-4 bg-gray-200 rounded w-full"></div>
    </div>
  </div>
));

const SearchSkeleton = memo(({ count = 3, type = "user" }) => (
  <div className="space-y-4">
    {Array.from({ length: count }, (_, i) => 
      type === "user" ? (
        <LoadingSkeleton key={i} />
      ) : (
        <PostSkeleton key={i} />
      )
    )}
  </div>
));

export default SearchSkeleton;
export { LoadingSkeleton, PostSkeleton };