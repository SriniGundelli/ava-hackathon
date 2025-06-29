import { neon } from '@netlify/neon';

const sql = neon(); // automatically uses env NETLIFY_DATABASE_URL

export default async (request: Request) => {
  // Handle CORS
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    });
  }

  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  try {
    const body = await request.json();
    console.log('Voice webhook received:', body);

    // Log the call to database
    await sql`
      INSERT INTO call_logs (
        call_sid,
        from_number,
        to_number,
        call_status,
        webhook_data,
        created_at
      ) VALUES (
        ${body.CallSid || ''},
        ${body.From || ''},
        ${body.To || ''},
        ${body.CallStatus || ''},
        ${JSON.stringify(body)},
        NOW()
      )
    `;

    // Return TwiML response for voice handling
    const twimlResponse = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice">Thank you for calling Ava AI Talent Assistant. Please hold while we connect you to our AI agent.</Say>
  <Redirect>${process.env.ELEVENLABS_SIP_URL || ''}</Redirect>
</Response>`;

    return new Response(twimlResponse, {
      status: 200,
      headers: {
        'Content-Type': 'text/xml',
        'Access-Control-Allow-Origin': '*',
      },
    });

  } catch (error) {
    console.error('Voice webhook error:', error);
    
    const errorTwiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice">We're sorry, but we're experiencing technical difficulties. Please try calling back later.</Say>
  <Hangup/>
</Response>`;

    return new Response(errorTwiml, {
      status: 500,
      headers: {
        'Content-Type': 'text/xml',
        'Access-Control-Allow-Origin': '*',
      },
    });
  }
};