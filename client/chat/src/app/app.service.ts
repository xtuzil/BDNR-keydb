import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { HttpClient } from '@angular/common/http';

export interface Message {
  author: string;
  timestamp: string;
  text: string;
  id: string;
}

@Injectable({
  providedIn: 'root',
})
export class AppService {
  message: Subject<Message> = new Subject<Message>();

  rooms: Subject<string[]> = new Subject<string[]>();
  chatMessages: Subject<Message[]> = new Subject<Message[]>();

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
      });
    };
  }

  fetchUserRooms(username: string): void {
    this.http
      .get(`http://127.0.0.1:8000/users/${username}/rooms/`)
      .pipe()
      .subscribe((data: any) => {
        this.rooms.next(data ?? []);
      });
  }

  fetchRoomMessages(room_code: string): void {
    this.http
      .get(`http://127.0.0.1:8000/rooms/${room_code}/messages/`)
      .pipe()
      .subscribe((data: any) => {
        this.chatMessages.next(data ?? []);
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
}
