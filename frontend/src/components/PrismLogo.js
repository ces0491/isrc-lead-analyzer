// src/components/PrismLogo.js

import React from 'react';

const PrismLogo = ({ 
  className = "h-8 w-32", 
  variant = "auto", // "auto", "light", "dark", "red"
  showSubtext = true,
  animated = false
}) => {
  
  const getColors = () => {
    switch (variant) {
      case "light":
        return {
          primary: "#1A1A1A",
          secondary: "#333333", 
          accent: "#E50914",
          text: "#1A1A1A",
          subtext: "#666666"
        };
      case "dark":
        return {
          primary: "#FFFFFF",
          secondary: "#F8F9FA",
          accent: "#E50914", 
          text: "#FFFFFF",
          subtext: "#F8F9FA"
        };
      case "red":
        return {
          primary: "#FFFFFF",
          secondary: "#F8F9FA",
          accent: "#1A1A1A",
          text: "#FFFFFF", 
          subtext: "#FFFFFF"
        };
      default: // auto - adapts to current text color
        return {
          primary: "currentColor",
          secondary: "currentColor",
          accent: "#E50914",
          text: "currentColor",
          subtext: "currentColor"
        };
    }
  };
  
  const colors = getColors();
  const gradientId = `prismGrad-${Math.random().toString(36).substr(2, 9)}`;
  
  return (
    <div className={`${className} flex items-center justify-center`}>
      <svg viewBox="0 0 200 80" className="w-full h-full" role="img" aria-label="PRISM Analytics Engine">
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style={{ stopColor: colors.primary }} />
            <stop offset="100%" style={{ stopColor: colors.secondary }} />
          </linearGradient>
        </defs>
        
        {/* Musical Notes Input - representing raw music data */}
        <g className={animated ? "animate-pulse" : ""}>
          {/* Staff lines */}
          <line x1="5" y1="20" x2="30" y2="20" stroke={colors.secondary} strokeWidth="0.5" opacity="0.6"/>
          <line x1="5" y1="24" x2="30" y2="24" stroke={colors.secondary} strokeWidth="0.5" opacity="0.6"/>
          <line x1="5" y1="28" x2="30" y2="28" stroke={colors.secondary} strokeWidth="0.5" opacity="0.6"/>
          <line x1="5" y1="32" x2="30" y2="32" stroke={colors.secondary} strokeWidth="0.5" opacity="0.6"/>
          <line x1="5" y1="36" x2="30" y2="36" stroke={colors.secondary} strokeWidth="0.5" opacity="0.6"/>
          
          {/* Musical notes */}
          <circle cx="10" cy="22" r="1.5" fill={colors.secondary}/>
          <circle cx="18" cy="30" r="1.5" fill={colors.secondary}/>
          <circle cx="25" cy="26" r="1.5" fill={colors.secondary}/>
          
          {/* Note stems */}
          <line x1="11.5" y1="22" x2="11.5" y2="15" stroke={colors.secondary} strokeWidth="1"/>
          <line x1="19.5" y1="30" x2="19.5" y2="23" stroke={colors.secondary} strokeWidth="1"/>
          <line x1="26.5" y1="26" x2="26.5" y2="19" stroke={colors.secondary} strokeWidth="1"/>
        </g>
        
        {/* Triangular Prism - 3D processing engine */}
        <g className={animated ? "animate-pulse" : ""}>
          {/* Front face - main triangle */}
          <polygon 
            points="50,15 35,45 65,45" 
            fill={`url(#${gradientId})`} 
            stroke={colors.primary} 
            strokeWidth="1.5"
          />
          
          {/* Back face - offset triangle for 3D effect */}
          <polygon 
            points="55,12 40,42 70,42" 
            fill={colors.primary} 
            stroke={colors.primary} 
            strokeWidth="1" 
            opacity="0.9"
          />
          
          {/* Connecting edges to create 3D depth */}
          <line x1="50" y1="15" x2="55" y2="12" stroke={colors.primary} strokeWidth="1.5"/>
          <line x1="35" y1="45" x2="40" y2="42" stroke={colors.primary} strokeWidth="1.5"/>
          <line x1="65" y1="45" x2="70" y2="42" stroke={colors.primary} strokeWidth="1.5"/>
          
          {/* Analytics processing lines through the prism */}
          <line x1="42" y1="32" x2="58" y2="29" stroke={colors.accent} strokeWidth="2.5">
            {animated && (
              <animate attributeName="opacity" values="0.5;1;0.5" dur="1.5s" repeatCount="indefinite"/>
            )}
          </line>
          <line x1="45" y1="38" x2="61" y2="35" stroke={colors.accent} strokeWidth="2" opacity="0.8">
            {animated && (
              <animate attributeName="opacity" values="1;0.3;1" dur="1.8s" repeatCount="indefinite"/>
            )}
          </line>
        </g>
        
        {/* Sin Wave Analytics Output - representing refined insights */}
        <g className={animated ? "animate-pulse" : ""}>
          {/* Primary analytics wave */}
          <path 
            d="M75,20 Q85,15 95,20 Q105,25 115,20 Q125,15 135,20 Q145,25 155,20 Q165,15 175,20" 
            stroke={colors.accent} 
            strokeWidth="2.5" 
            fill="none"
          >
            {animated && (
              <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite"/>
            )}
          </path>
          
          {/* Secondary analytics wave */}
          <path 
            d="M75,30 Q85,25 95,30 Q105,35 115,30 Q125,25 135,30 Q145,35 155,30 Q165,25 175,30" 
            stroke={colors.accent} 
            strokeWidth="2" 
            fill="none" 
            opacity="0.7"
          >
            {animated && (
              <animate attributeName="opacity" values="1;0.3;1" dur="2.2s" repeatCount="indefinite"/>
            )}
          </path>
          
          {/* Tertiary analytics wave */}
          <path 
            d="M75,40 Q85,35 95,40 Q105,45 115,40 Q125,35 135,40 Q145,45 155,40 Q165,35 175,40" 
            stroke={colors.accent} 
            strokeWidth="1.5" 
            fill="none" 
            opacity="0.5"
          >
            {animated && (
              <animate attributeName="opacity" values="0.6;1;0.6" dur="1.8s" repeatCount="indefinite"/>
            )}
          </path>
          
          {/* Insight data points */}
          <circle cx="85" cy="17" r="1.5" fill={colors.accent}>
            {animated && (
              <animate attributeName="r" values="1;2;1" dur="2s" repeatCount="indefinite"/>
            )}
          </circle>
          <circle cx="115" cy="23" r="1.5" fill={colors.accent}>
            {animated && (
              <animate attributeName="r" values="1.5;1;1.5" dur="1.7s" repeatCount="indefinite"/>
            )}
          </circle>
          <circle cx="145" cy="17" r="1.5" fill={colors.accent}>
            {animated && (
              <animate attributeName="r" values="1;2;1" dur="2.3s" repeatCount="indefinite"/>
            )}
          </circle>
        </g>
        
        {/* PRISM Text */}
        <text 
          x="100" 
          y="65" 
          textAnchor="middle" 
          fontFamily="Arial, sans-serif" 
          fontSize="14" 
          fontWeight="500" 
          letterSpacing="3px" 
          fill={colors.text}
          className="tracking-widest"
        >
          PRISM
        </text>
        
        {/* Analytics Engine Subtext */}
        {showSubtext && (
          <text 
            x="100" 
            y="75" 
            textAnchor="middle" 
            fontFamily="Arial, sans-serif" 
            fontSize="8" 
            fontWeight="400" 
            letterSpacing="1px" 
            fill={colors.subtext}
            className="tracking-wide"
          >
            ANALYTICS ENGINE
          </text>
        )}
      </svg>
    </div>
  );
};

export default PrismLogo;