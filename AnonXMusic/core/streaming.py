    import asyncio
    import logging

    # Config logging (if not already configured elsewhere)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


    async def stream_audio_chunk(writer, audio_chunk):
        """Sends a single chunk of audio over the socket, handling errors."""
        try:
            writer.write(audio_chunk)
            await writer.drain()
            logging.info("Audio chunk sent successfully.")
            return True
        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            logging.error(f"Network error encountered when streaming: {e}")
            if writer:
                try:
                   writer.close()
                   await writer.wait_closed()
                   logging.info("Socket closed")
                except Exception as close_e:
                   logging.error(f"Error closing socket {close_e}")
            return False
        except Exception as e:
            logging.error(f"Error during socket send: {e}")
            return False


    async def stream_audio_data(audio_data_generator, reader, writer):
        """Streams audio data from a generator function."""
        try:
            async for audio_chunk in audio_data_generator():
                data_sent = await stream_audio_chunk(writer,audio_chunk)
                if not data_sent:
                    return

        except Exception as e:
             logging.error(f"Error during streaming: {e}")
             if writer:
                writer.close()
                await writer.wait_closed()
                logging.info("Connection closed")
