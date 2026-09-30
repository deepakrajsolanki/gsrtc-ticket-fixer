export default async function handler(req, res) {
  // Global CORS Headers
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,POST');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Content-Type'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  let targetUrl = '';
  if (req.body) {
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch(e) {}
    }
    if (body.url) targetUrl = body.url;
    else if (body.b64) {
      try { targetUrl = Buffer.from(body.b64, 'base64').toString('utf-8'); } catch(e) {}
    }
  }

  if (!targetUrl && req.query) {
    if (req.query.url) targetUrl = req.query.url;
    else if (req.query.b64) {
      try { targetUrl = Buffer.from(req.query.b64, 'base64').toString('utf-8'); } catch(e) {}
    }
  }

  targetUrl = (targetUrl || '').trim();

  // Support shorthand or relative URLs
  if (targetUrl.startsWith('viewTicket.do') || targetUrl.startsWith('/OPRSOnline/') || targetUrl.startsWith('VTKT=')) {
    if (targetUrl.startsWith('VTKT=')) {
      targetUrl = 'https://www.gsrtc.in/OPRSOnline/viewTicket.do?' + targetUrl;
    } else if (targetUrl.startsWith('/')) {
      targetUrl = 'https://www.gsrtc.in' + targetUrl;
    } else {
      targetUrl = 'https://www.gsrtc.in/OPRSOnline/' + targetUrl;
    }
  }

  if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
    targetUrl = 'https://' + targetUrl;
  }

  if (!targetUrl.includes('gsrtc.in')) {
    return res.status(400).json({ error: 'Invalid URL. Only gsrtc.in URLs are accepted.' });
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 12000);

    const response = await fetch(targetUrl, {
      signal: controller.signal,
      redirect: 'follow',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.gsrtc.in/',
        'Cache-Control': 'no-cache'
      }
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      return res.status(502).json({ error: `GSRTC returned status ${response.status}` });
    }

    const html = await response.text();
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    return res.status(200).send(html);
  } catch (err) {
    return res.status(502).json({ error: `Failed to fetch ticket from GSRTC: ${err.message}` });
  }
}
