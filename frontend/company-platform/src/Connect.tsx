import { useEffect, useState } from 'react'

type Channel = { id: string; channel_type: string; name: string; visibility: string; created_at: string }
type Message = { id: string; sender_identity_id: string; content: string; created_at: string }

type ApiResponse<T> = { data?: T; request_id?: string }

async function api<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    credentials: 'include',
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
  })
  const body = await response.json().catch(() => ({})) as ApiResponse<T> & { message?: string }
  if (!response.ok) throw new Error(body.message || 'Phoenix Core request failed.')
  return body.data as T
}

export function Connect() {
  const [channels, setChannels] = useState<Channel[]>([])
  const [activeId, setActiveId] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [draft, setDraft] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [notice, setNotice] = useState('')

  const loadChannels = async () => {
    setLoading(true); setNotice('')
    try {
      const result = await api<Channel[]>('/api/v1/connect/channels')
      setChannels(result ?? [])
      if (!activeId && result?.[0]) setActiveId(result[0].id)
      if (activeId && !result?.some(channel => channel.id === activeId)) setActiveId(result?.[0]?.id ?? '')
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to load Connect.') }
    finally { setLoading(false) }
  }

  const loadMessages = async (channelId: string) => {
    if (!channelId) return
    try {
      const result = await api<{ items: Message[] }>(`/api/v1/connect/channels/${channelId}/messages?limit=100`)
      setMessages([...(result?.items ?? [])].reverse())
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to load messages.') }
  }

  useEffect(() => { void loadChannels() }, [])
  useEffect(() => { if (activeId) void loadMessages(activeId) }, [activeId])

  const send = async () => {
    if (!activeId || !draft.trim() || sending) return
    setSending(true); setNotice('')
    try {
      await api(`/api/v1/connect/channels/${activeId}/messages`, { method: 'POST', body: JSON.stringify({ content: draft.trim() }) })
      setDraft('')
      await loadMessages(activeId)
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to send message.') }
    finally { setSending(false) }
  }

  const active = channels.find(channel => channel.id === activeId)
  return <div className="connect-page">
    <div className="connect-toolbar"><div><span className="section-label">PHOENIX CONNECT</span><h3>Company communication</h3></div><button className="refresh-button" onClick={() => void loadChannels()}>Refresh</button></div>
    <div className="connect-shell">
      <aside className="connect-channels"><div className="connect-heading">CONVERSATIONS</div>{loading ? <div className="connect-empty">Loading…</div> : channels.length === 0 ? <div className="connect-empty">No conversations yet.</div> : channels.map(channel => <button key={channel.id} className={`connect-channel ${activeId === channel.id ? 'active' : ''}`} onClick={() => setActiveId(channel.id)}><span className="connect-channel-dot" /><span><strong>{channel.name}</strong><small>{channel.channel_type}</small></span></button>)}</aside>
      <section className="connect-conversation">{active ? <><header className="connect-conversation-header"><div><strong>{active.name}</strong><span>{active.channel_type} · {active.visibility}</span></div></header><div className="connect-messages">{messages.length === 0 ? <div className="connect-empty">No messages in this conversation.</div> : messages.map(message => <article className="connect-message" key={message.id}><div className="connect-message-avatar">{message.sender_identity_id.slice(0, 2).toUpperCase()}</div><div><div className="connect-message-meta"><strong>{message.sender_identity_id.slice(0, 8)}</strong><time>{new Date(message.created_at).toLocaleString()}</time></div><p>{message.content}</p></div></article>)}</div><div className="connect-composer"><input value={draft} onChange={event => setDraft(event.target.value)} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); void send() } }} placeholder="Write a message…" disabled={sending} /><button className="primary-action" onClick={() => void send()} disabled={sending || !draft.trim()}>{sending ? 'Sending…' : 'Send'}</button></div></> : <div className="connect-empty">Select a conversation to begin.</div>}</section>
    </div>
    {notice && <div className="inline-notice">{notice}</div>}
  </div>
}
