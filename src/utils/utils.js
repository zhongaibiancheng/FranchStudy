/**
 * 生成随机字符串
 * @param {number} length - 字符串长度
 * @returns {string} 随机字符串
 */
export function generateRandomString(length) {
  const characters = '#!^&*%()@ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  
  for (let i = 0; i < length; i++) {
    const randomIndex = Math.floor(Math.random() * characters.length);
    result += characters.charAt(randomIndex);
  }
  
  return result;
}

/**
 * 生成随机电子邮箱
 * @param {number} usernameLength - 用户名长度（默认6-12位）
 * @param {string} domain - 指定域名（可选）
 * @returns {string} 随机邮箱地址
 */
export function generateRandomEmail(usernameLength = null, domain = null) {
  // 常用邮箱域名
  const commonDomains = [
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
    'icloud.com', 'aol.com', 'protonmail.com', 'qq.com',
    '163.com', '126.com', 'sina.com', 'sohu.com'
  ];
  
  // 随机用户名字符集（避免特殊字符）
  const usernameChars = 'abcdefghijklmnopqrstuvwxyz0123456789._-';
  
  // 生成用户名长度（6-12位）
  const nameLength = usernameLength || Math.floor(Math.random() * 7) + 6;
  
  // 生成随机用户名
  let username = '';
  for (let i = 0; i < nameLength; i++) {
    const randomIndex = Math.floor(Math.random() * usernameChars.length);
    username += usernameChars.charAt(randomIndex);
  }
  
  // 确保用户名不以点、下划线或连字符开头或结尾
  username = username.replace(/^[._-]|[._-]$/g, '');
  
  // 选择域名
  const selectedDomain = domain || commonDomains[Math.floor(Math.random() * commonDomains.length)];
  
  return `${username}@${selectedDomain}`;
}

