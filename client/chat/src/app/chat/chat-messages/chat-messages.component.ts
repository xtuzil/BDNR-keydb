import { ChangeDetectorRef, Component, Input, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { AppService, Message } from 'src/app/app.service';

@Component({
  selector: 'app-chat-messages',
  templateUrl: './chat-messages.component.html',
  styleUrls: ['./chat-messages.component.scss'],
})
export class ChatMessagesComponent implements OnInit {
  @Input()
  messages: Message[] = [];

  @Input()
  roomCode: string = '';

  protected messageStreamSub: Subscription | undefined;

  constructor(private service: AppService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    if (this.roomCode) {
      this.subscribeStream();
    }
  }

  protected subscribeStream(): void {
    this.messageStreamSub = this.service.message.subscribe((msg) => {
      if (msg.room_code === this.roomCode) {
        this.messages = [msg, ...this.messages];
        this.cdr.detectChanges();
        console.log('NEW MESSAGES: ', this.messages);
      }
    });
  }

  ngOnDestroy(): void {
    this.messageStreamSub?.unsubscribe();
  }
}
