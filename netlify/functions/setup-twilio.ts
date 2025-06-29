import { neon } from '@netlify/neon';

const sql = neon(); // automatically uses env NETLIFY_DATABASE_URL

interface TwilioSetupRequest {
  friendlyName: string;
  elevenLabsDomain: string;
  voiceWebhookUrl: string;
}

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
    const { default: twilio } = await import('twilio');
    
    const accountSid = process.env.TWILIO_ACCOUNT_SID;
    const authToken = process.env.TWILIO_AUTH_TOKEN;

    if (!accountSid || !authToken) {
      throw new Error('Twilio credentials not configured');
    }

    const client = twilio(accountSid, authToken);
    const body: TwilioSetupRequest = await request.json();
    const { friendlyName, elevenLabsDomain, voiceWebhookUrl } = body;

    // Create SIP trunk
    const trunk = await client.trunking.v1.trunks.create({
      friendlyName,
      domainName: `${friendlyName.toLowerCase().replace(/\s+/g, '-')}.sip.twilio.com`,
    });

    // Create origination URL with proper SIP URI
    const elevenLabsSipUri = `sip:${elevenLabsDomain}.sip.11.ai`;
    
    await client.trunking.v1
      .trunks(trunk.sid)
      .originationUrls
      .create({
        friendlyName: 'ElevenLabs Voice Handler',
        sipUrl: elevenLabsSipUri,
        priority: 10,
        weight: 10,
        enabled: true,
      });

    // Purchase phone number with area code fallback
    let phoneNumber;
    try {
      const availableNumbers = await client.availablePhoneNumbers('US')
        .local
        .list({ areaCode: 415, limit: 1 });

      if (availableNumbers.length === 0) {
        // Fallback to any available number
        const anyNumbers = await client.availablePhoneNumbers('US')
          .local
          .list({ limit: 1 });
        
        if (anyNumbers.length === 0) {
          throw new Error('No phone numbers available');
        }
        
        phoneNumber = await client.incomingPhoneNumbers.create({
          phoneNumber: anyNumbers[0].phoneNumber,
          voiceTrunkSid: trunk.sid,
          voiceUrl: voiceWebhookUrl,
          voiceMethod: 'POST',
        });
      } else {
        phoneNumber = await client.incomingPhoneNumbers.create({
          phoneNumber: availableNumbers[0].phoneNumber,
          voiceTrunkSid: trunk.sid,
          voiceUrl: voiceWebhookUrl,
          voiceMethod: 'POST',
        });
      }
    } catch (error) {
      console.error('Phone number purchase failed:', error);
      throw new Error('Failed to purchase phone number');
    }

    // Store setup in database
    await sql`
      INSERT INTO twilio_setup (
        trunk_sid,
        phone_number,
        friendly_name,
        elevenlabs_domain,
        voice_webhook_url,
        created_at
      ) VALUES (
        ${trunk.sid},
        ${phoneNumber.phoneNumber},
        ${friendlyName},
        ${elevenLabsDomain},
        ${voiceWebhookUrl},
        NOW()
      )
    `;

    return new Response(JSON.stringify({
      success: true,
      setup: {
        trunkSid: trunk.sid,
        phoneNumber: phoneNumber.phoneNumber,
        voiceWebhookUrl,
        elevenLabsSipUri,
      },
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    });

  } catch (error) {
    console.error('Twilio setup error:', error);
    
    return new Response(JSON.stringify({
      error: 'Setup failed',
      message: error instanceof Error ? error.message : 'Unknown error',
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    });
  }
};