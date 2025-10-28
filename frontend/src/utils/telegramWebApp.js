// Telegram WebApp utility functions

export const isTelegramWebApp = () => {
  return typeof window !== 'undefined' && window.Telegram?.WebApp?.initData;
};

export const getTelegramWebApp = () => {
  if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
    return window.Telegram.WebApp;
  }
  return null;
};

export const getTelegramUser = () => {
  const webApp = getTelegramWebApp();
  if (webApp && webApp.initDataUnsafe?.user) {
    return webApp.initDataUnsafe.user;
  }
  return null;
};

export const getTelegramInitData = () => {
  const webApp = getTelegramWebApp();
  return webApp?.initData || '';
};

export const expandTelegramWebApp = () => {
  const webApp = getTelegramWebApp();
  if (webApp) {
    webApp.expand();
    webApp.ready();
  }
};

export const closeTelegramWebApp = () => {
  const webApp = getTelegramWebApp();
  if (webApp) {
    webApp.close();
  }
};
