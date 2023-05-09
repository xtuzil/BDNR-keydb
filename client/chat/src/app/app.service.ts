import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { HttpClient } from '@angular/common/http';

export interface Message {
  author: string;
  timestamp: string;
  text: string;
  id: string;
  room_code?: string;
}

export interface Room {
  name: string;
  code: string;
  lastMessage?: string;
}

@Injectable({
  providedIn: 'root',
})
export class AppService {
  message: Subject<Message> = new Subject<Message>();
  rooms: Subject<Room[]> = new Subject<Room[]>();
  chatMessages: Subject<Message[]> = new Subject<Message[]>();
  searchedMessages: Subject<Message[]> = new Subject<Message[]>();

  constructor(private http: HttpClient) {}

  getMessagesStream(): void {
    let source = new EventSource('http://127.0.0.1:8000/stream');
    source.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log('MESSAGE: ', message);
      this.message.next({
        author: message.author,
        timestamp: message.time,
        text: message.text,
        id: 'TODO',
        room_code: message.room_code,
      });
    };
  }

  fetchUserRooms(username: string): void {
    this.http
      .get(`http://127.0.0.1:8000/users/${username}/rooms/`)
      .pipe()
      .subscribe((data: any) => {
        console.log('Rooms: ', data);
        this.rooms.next(data ?? []);
      });
  }

  fetchRoomMessages(room_code: string): void {
    this.http
      .get(`http://127.0.0.1:8000/rooms/${room_code}/messages/`)
      .pipe()
      .subscribe((data: any) => {
        this.chatMessages.next(data);
      });
  }

  searchInRoom(room_code: string, search_word: string): void {
    this.http
      .get(`http://127.0.0.1:8000/rooms/${room_code}/messages?q=${search_word}`)
      .pipe()
      .subscribe((data: any) => {
        this.searchedMessages.next(data);
      });
  }

  search(search_word: string): void {
    const username = localStorage.getItem('Username') ?? '';
    this.http
      .get(
        `http://127.0.0.1:8000/users/${username}/rooms/messages?q=${search_word}`
      )
      .pipe()
      .subscribe((data: any) => {
        this.searchedMessages.next(data);
      });
  }

  sendMessage(room_code: string, message: string): void {
    const username = localStorage.getItem('Username') ?? '';
    this.http
      .post(`http://127.0.0.1:8000/rooms/${room_code}/messages/`, {
        text: message,
        author: username,
      })
      .pipe()
      .subscribe((data: any) => {});
  }

  createRoom(room_name: string): Observable<any> {
    const username = localStorage.getItem('Username') ?? '';
    return this.http.post(`http://127.0.0.1:8000/rooms/`, {
      name: room_name,
      author: username,
    });
  }

  joinRoom(room_code: string): Observable<any> {
    const username = localStorage.getItem('Username') ?? '';
    return this.http.post(`http://127.0.0.1:8000/rooms/register`, {
      room_code: room_code,
      user: username,
    });
  }
}
