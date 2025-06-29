import { neon } from '@netlify/neon';

const sql = neon(); // automatically uses env NETLIFY_DATABASE_URL

interface ScheduleCallRequest {
  candidate_name: string;
  candidate_email: string;
  candidate_phone?: string;
  time_zone?: string;
}

interface CalComSlot {
  time: string;
  attendees: number;
  bookingUid: string;
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
    const body: ScheduleCallRequest = await request.json();
    const { candidate_name, candidate_email, candidate_phone, time_zone = 'America/New_York' } = body;

    if (!candidate_name || !candidate_email) {
      return new Response(JSON.stringify({ 
        error: 'Missing required fields: candidate_name and candidate_email' 
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Get available slots from Cal.com
    const calcomApiKey = process.env.CALCOM_API_KEY;
    if (!calcomApiKey) {
      throw new Error('CALCOM_API_KEY not configured');
    }

    const slotsResponse = await fetch('https://api.cal.com/v2/slots/available', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${calcomApiKey}`,
        'Content-Type': 'application/json',
      },
    });

    if (!slotsResponse.ok) {
      throw new Error(`Cal.com API error: ${slotsResponse.status}`);
    }

    const slotsData = await slotsResponse.json();
    const availableSlots = slotsData.slots || [];

    if (availableSlots.length === 0) {
      return new Response(JSON.stringify({
        error: 'No available slots found',
        message: 'Please try again later or contact us directly'
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Book the first available slot
    const selectedSlot = availableSlots[0];
    const bookingResponse = await fetch('https://api.cal.com/v2/bookings', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${calcomApiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        start: selectedSlot.time,
        eventTypeId: process.env.CALCOM_EVENT_TYPE_ID || 1,
        attendee: {
          name: candidate_name,
          email: candidate_email,
          timeZone: time_zone,
        },
        metadata: {
          phone: candidate_phone,
          source: 'ava-ai-assistant',
        },
      }),
    });

    if (!bookingResponse.ok) {
      const errorData = await bookingResponse.json();
      throw new Error(`Booking failed: ${JSON.stringify(errorData)}`);
    }

    const bookingData = await bookingResponse.json();

    // Store the booking in database
    await sql`
      INSERT INTO bookings (
        candidate_name,
        candidate_email,
        candidate_phone,
        scheduled_time,
        booking_uid,
        meeting_url,
        time_zone,
        created_at
      ) VALUES (
        ${candidate_name},
        ${candidate_email},
        ${candidate_phone || null},
        ${selectedSlot.time},
        ${bookingData.uid},
        ${bookingData.meetingUrl || ''},
        ${time_zone},
        NOW()
      )
    `;

    return new Response(JSON.stringify({
      success: true,
      booking: {
        candidate_name,
        candidate_email,
        scheduled_time: selectedSlot.time,
        meeting_url: bookingData.meetingUrl,
        booking_uid: bookingData.uid,
      },
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    });

  } catch (error) {
    console.error('Schedule call error:', error);
    
    return new Response(JSON.stringify({
      error: 'Internal server error',
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